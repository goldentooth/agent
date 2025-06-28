"""Test-driven development for agent lifecycle management.

This module implements tests for the core agent lifecycle states and transitions,
following the narrative-driven approach outlined in RECURSIVE_AGENT_PROPOSAL.md.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

import pytest
from pydantic import BaseModel, Field

from goldentooth_agent.core.recursive_agents.lifecycle import (
    AgentIdentity,
    AgentLifecycle,
    AgentState,
    LifecycleManager,
    LifecycleTransition,
    LifecycleError,
)


class TestAgentIdentity:
    """Test agent identity and lineage tracking."""
    
    def test_agent_identity_creation(self):
        """Test creating a new agent identity with full lineage."""
        # Given: A parent agent ID and narrative role
        parent_id = "patriarch-001"
        
        # When: Creating a new agent identity
        identity = AgentIdentity(
            id="child-001",
            name="Ambitious Heir",
            creator_id=parent_id,
            birth_time=datetime.utcnow(),
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=[parent_id, "grandparent-001"],
            narrative_role="ambitious_heir"
        )
        
        # Then: Identity should track its heritage
        assert identity.creator_id == parent_id
        assert parent_id in identity.lineage
        assert identity.narrative_role == "ambitious_heir"
        assert identity.lifecycle == AgentLifecycle.PERSISTENT
    
    def test_ephemeral_agent_identity(self):
        """Test ephemeral agents have limited lifecycle."""
        # Given: An ephemeral agent configuration
        
        # When: Creating an ephemeral agent
        identity = AgentIdentity(
            id="messenger-001",
            name="Swift Messenger",
            creator_id="summoner-001",
            birth_time=datetime.utcnow(),
            lifecycle=AgentLifecycle.EPHEMERAL,
            lineage=["summoner-001"],
            narrative_role="messenger"
        )
        
        # Then: Agent should be marked as ephemeral
        assert identity.lifecycle == AgentLifecycle.EPHEMERAL
        assert identity.is_ephemeral()
        assert not identity.is_persistent()
    
    def test_agent_age_calculation(self):
        """Test agent age calculation for narrative purposes."""
        # Given: An agent born in the past
        birth_time = datetime.utcnow() - timedelta(days=30)
        
        # When: Creating the agent
        identity = AgentIdentity(
            id="elder-001",
            name="Elder Sage",
            creator_id=None,  # Original agent
            birth_time=birth_time,
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=[],
            narrative_role="wise_elder"
        )
        
        # Then: Age should be calculable
        assert identity.age_in_days() >= 30
        assert identity.is_elder(threshold_days=20)
        assert not identity.is_newborn(threshold_hours=1)


class TestAgentLifecycle:
    """Test agent lifecycle states and transitions."""
    
    def test_lifecycle_state_transitions(self):
        """Test valid lifecycle state transitions."""
        # Given: Lifecycle states
        
        # When/Then: Checking valid transitions
        assert AgentLifecycle.can_transition(
            AgentLifecycle.EPHEMERAL,
            AgentLifecycle.ARCHIVED
        )
        assert AgentLifecycle.can_transition(
            AgentLifecycle.PERSISTENT,
            AgentLifecycle.DORMANT
        )
        assert AgentLifecycle.can_transition(
            AgentLifecycle.DORMANT,
            AgentLifecycle.PERSISTENT
        )
        assert not AgentLifecycle.can_transition(
            AgentLifecycle.ARCHIVED,
            AgentLifecycle.PERSISTENT
        )
    
    def test_lifecycle_state_properties(self):
        """Test lifecycle state properties."""
        # Given: Different lifecycle states
        
        # When/Then: Checking properties
        assert AgentLifecycle.EPHEMERAL.is_active()
        assert AgentLifecycle.PERSISTENT.is_active()
        assert not AgentLifecycle.DORMANT.is_active()
        assert not AgentLifecycle.ARCHIVED.is_active()
        
        assert AgentLifecycle.PERSISTENT.can_store_state()
        assert AgentLifecycle.DORMANT.can_store_state()
        assert not AgentLifecycle.EPHEMERAL.can_store_state()


class TestLifecycleManager:
    """Test the lifecycle manager that handles agent state transitions."""
    
    @pytest.fixture
    def lifecycle_manager(self):
        """Create a lifecycle manager for testing."""
        return LifecycleManager()
    
    @pytest.fixture
    def sample_agent(self):
        """Create a sample agent for testing."""
        return AgentIdentity(
            id="test-agent-001",
            name="Test Agent",
            creator_id=None,
            birth_time=datetime.utcnow(),
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=[],
            narrative_role="test_subject"
        )
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, lifecycle_manager, sample_agent):
        """Test registering a new agent with the lifecycle manager."""
        # When: Registering the agent
        await lifecycle_manager.register_agent(sample_agent)
        
        # Then: Agent should be tracked
        assert await lifecycle_manager.agent_exists(sample_agent.id)
        state = await lifecycle_manager.get_agent_state(sample_agent.id)
        assert state.lifecycle == AgentLifecycle.PERSISTENT
        assert state.is_active
    
    @pytest.mark.asyncio
    async def test_ephemeral_agent_cleanup(self, lifecycle_manager):
        """Test that ephemeral agents are cleaned up after use."""
        # Given: An ephemeral agent
        ephemeral = AgentIdentity(
            id="ephemeral-001",
            name="Temporary Messenger",
            creator_id="summoner-001",
            birth_time=datetime.utcnow(),
            lifecycle=AgentLifecycle.EPHEMERAL,
            lineage=["summoner-001"],
            narrative_role="messenger"
        )
        
        # When: Registering and using the agent
        await lifecycle_manager.register_agent(ephemeral)
        assert await lifecycle_manager.agent_exists(ephemeral.id)
        
        # When: Marking the agent as used
        await lifecycle_manager.mark_ephemeral_complete(ephemeral.id)
        
        # Then: Agent should be archived
        state = await lifecycle_manager.get_agent_state(ephemeral.id)
        assert state.lifecycle == AgentLifecycle.ARCHIVED
        assert not state.is_active
    
    @pytest.mark.asyncio
    async def test_persistent_to_dormant_transition(self, lifecycle_manager, sample_agent):
        """Test transitioning a persistent agent to dormant state."""
        # Given: A registered persistent agent
        await lifecycle_manager.register_agent(sample_agent)
        
        # When: Transitioning to dormant
        transition = await lifecycle_manager.transition(
            sample_agent.id,
            AgentLifecycle.DORMANT,
            reason="Agent entering hibernation"
        )
        
        # Then: Transition should be recorded
        assert transition.from_state == AgentLifecycle.PERSISTENT
        assert transition.to_state == AgentLifecycle.DORMANT
        assert transition.reason == "Agent entering hibernation"
        
        # And: Agent state should be updated
        state = await lifecycle_manager.get_agent_state(sample_agent.id)
        assert state.lifecycle == AgentLifecycle.DORMANT
        assert not state.is_active
    
    @pytest.mark.asyncio
    async def test_dormant_reactivation(self, lifecycle_manager):
        """Test reactivating a dormant agent with narrative context."""
        # Given: A dormant agent
        dormant = AgentIdentity(
            id="sleeping-beauty-001",
            name="Sleeping Beauty",
            creator_id=None,
            birth_time=datetime.utcnow() - timedelta(days=100),
            lifecycle=AgentLifecycle.DORMANT,
            lineage=[],
            narrative_role="cursed_princess"
        )
        await lifecycle_manager.register_agent(dormant)
        
        # When: A prince attempts to wake the agent
        awakener_id = "prince-charming-001"
        transition = await lifecycle_manager.reactivate_dormant(
            dormant.id,
            awakener_id=awakener_id,
            narrative_event="true_loves_kiss"
        )
        
        # Then: Agent should be active again
        assert transition.to_state == AgentLifecycle.PERSISTENT
        assert transition.metadata["awakener_id"] == awakener_id
        assert transition.metadata["narrative_event"] == "true_loves_kiss"
        
        state = await lifecycle_manager.get_agent_state(dormant.id)
        assert state.is_active
    
    @pytest.mark.asyncio
    async def test_agent_death_and_archival(self, lifecycle_manager, sample_agent):
        """Test agent death becomes a narrative event."""
        # Given: A living agent
        await lifecycle_manager.register_agent(sample_agent)
        
        # When: The agent dies dramatically
        death_event = await lifecycle_manager.kill_agent(
            sample_agent.id,
            cause="betrayal_by_trusted_ally",
            killer_id="brutus-001",
            last_words="Et tu, Brute?"
        )
        
        # Then: Death should be recorded narratively
        assert death_event.lifecycle == AgentLifecycle.ARCHIVED
        assert death_event.death_cause == "betrayal_by_trusted_ally"
        assert death_event.killer_id == "brutus-001"
        assert death_event.last_words == "Et tu, Brute?"
        
        # And: Agent should be archived but remembered
        state = await lifecycle_manager.get_agent_state(sample_agent.id)
        assert state.lifecycle == AgentLifecycle.ARCHIVED
        assert not state.is_active
        assert state.death_metadata is not None
    
    @pytest.mark.asyncio
    async def test_invalid_lifecycle_transition(self, lifecycle_manager):
        """Test that invalid transitions are prevented."""
        # Given: An archived (dead) agent
        dead_agent = AgentIdentity(
            id="ghost-001",
            name="Restless Spirit",
            creator_id=None,
            birth_time=datetime.utcnow() - timedelta(days=365),
            lifecycle=AgentLifecycle.ARCHIVED,
            lineage=[],
            narrative_role="vengeful_ghost"
        )
        await lifecycle_manager.register_agent(dead_agent)
        
        # When: Attempting to revive the dead
        with pytest.raises(LifecycleError, match="Cannot transition from ARCHIVED"):
            await lifecycle_manager.transition(
                dead_agent.id,
                AgentLifecycle.PERSISTENT,
                reason="necromancy_attempt"
            )
    
    @pytest.mark.asyncio
    async def test_agent_genealogy_tracking(self, lifecycle_manager):
        """Test tracking agent family trees through generations."""
        # Given: A founding ancestor
        ancestor = AgentIdentity(
            id="founder-001",
            name="Dynasty Founder",
            creator_id=None,
            birth_time=datetime.utcnow() - timedelta(days=1000),
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=[],
            narrative_role="dynasty_founder"
        )
        await lifecycle_manager.register_agent(ancestor)
        
        # When: Creating three generations
        parent_id = ancestor.id
        family_tree = [ancestor]
        
        for generation in range(3):
            child = AgentIdentity(
                id=f"generation-{generation+1}-001",
                name=f"Heir of Generation {generation+1}",
                creator_id=parent_id,
                birth_time=datetime.utcnow() - timedelta(days=1000-(generation+1)*300),
                lifecycle=AgentLifecycle.PERSISTENT,
                lineage=family_tree[-1].lineage + [parent_id],
                narrative_role="heir"
            )
            await lifecycle_manager.register_agent(child)
            family_tree.append(child)
            parent_id = child.id
        
        # Then: Should be able to trace lineage
        descendants = await lifecycle_manager.get_descendants(ancestor.id)
        assert len(descendants) == 3
        
        # And: Should be able to find common ancestors
        youngest = family_tree[-1]
        ancestors = await lifecycle_manager.get_ancestors(youngest.id)
        assert ancestor.id in [a.id for a in ancestors]
        assert len(ancestors) == 3  # Parent, grandparent, great-grandparent
    
    @pytest.mark.asyncio
    async def test_concurrent_lifecycle_operations(self, lifecycle_manager):
        """Test that concurrent operations maintain consistency."""
        # Given: Multiple agents
        agents = []
        for i in range(10):
            agent = AgentIdentity(
                id=f"concurrent-{i:03d}",
                name=f"Concurrent Agent {i}",
                creator_id=None,
                birth_time=datetime.utcnow(),
                lifecycle=AgentLifecycle.PERSISTENT,
                lineage=[],
                narrative_role="test_subject"
            )
            agents.append(agent)
            await lifecycle_manager.register_agent(agent)
        
        # When: Performing concurrent transitions
        async def transition_agent(agent):
            await lifecycle_manager.transition(
                agent.id,
                AgentLifecycle.DORMANT,
                reason="mass_hibernation"
            )
        
        await asyncio.gather(*[transition_agent(a) for a in agents])
        
        # Then: All agents should be dormant
        for agent in agents:
            state = await lifecycle_manager.get_agent_state(agent.id)
            assert state.lifecycle == AgentLifecycle.DORMANT


class TestNarrativeLifecycleEvents:
    """Test narrative implications of lifecycle events."""
    
    @pytest.mark.asyncio
    async def test_death_triggers_inheritance(self, lifecycle_manager):
        """Test that agent death triggers inheritance mechanics."""
        # Given: A wealthy patriarch with three children
        patriarch = AgentIdentity(
            id="rich-patriarch-001",
            name="Wealthy Patriarch",
            creator_id=None,
            birth_time=datetime.utcnow() - timedelta(days=10000),
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=[],
            narrative_role="patriarch"
        )
        await lifecycle_manager.register_agent(patriarch)
        
        # And: Three children with different relationships
        children = []
        relationships = ["favorite", "black_sheep", "dutiful"]
        for i, rel in enumerate(relationships):
            child = AgentIdentity(
                id=f"child-{rel}-001",
                name=f"{rel.title()} Child",
                creator_id=patriarch.id,
                birth_time=datetime.utcnow() - timedelta(days=3000),
                lifecycle=AgentLifecycle.PERSISTENT,
                lineage=[patriarch.id],
                narrative_role=f"{rel}_child"
            )
            await lifecycle_manager.register_agent(child)
            children.append(child)
        
        # When: The patriarch dies
        death_event = await lifecycle_manager.kill_agent(
            patriarch.id,
            cause="natural_causes",
            last_words="The will is hidden in..."
        )
        
        # Then: Should trigger inheritance events
        inheritance_events = await lifecycle_manager.get_triggered_events(
            death_event.id,
            event_type="inheritance"
        )
        
        assert len(inheritance_events) > 0
        assert any(e.metadata.get("contested") for e in inheritance_events)
        
    @pytest.mark.asyncio
    async def test_dormancy_creates_mystery(self, lifecycle_manager):
        """Test that unexpected dormancy creates narrative mystery."""
        # Given: An active investigator
        investigator = AgentIdentity(
            id="detective-001",
            name="Keen Detective",
            creator_id=None,
            birth_time=datetime.utcnow() - timedelta(days=500),
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=[],
            narrative_role="investigator"
        )
        await lifecycle_manager.register_agent(investigator)
        
        # When: They suddenly go dormant without explanation
        transition = await lifecycle_manager.transition(
            investigator.id,
            AgentLifecycle.DORMANT,
            reason="mysterious_disappearance",
            metadata={
                "last_seen": "abandoned_warehouse",
                "investigating": "corruption_scandal",
                "left_behind": ["cryptic_note", "blood_stain"]
            }
        )
        
        # Then: Should create mystery storyline hooks
        mystery_hooks = await lifecycle_manager.get_narrative_hooks(
            transition.id,
            hook_type="mystery"
        )
        
        assert len(mystery_hooks) > 0
        assert any("missing_person" in h.tags for h in mystery_hooks)
        assert any("investigation_interrupted" in h.tags for h in mystery_hooks)