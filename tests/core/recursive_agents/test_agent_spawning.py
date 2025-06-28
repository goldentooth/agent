"""Test-driven development for agent spawning and inheritance.

This module tests the recursive agent spawning capabilities, including
trait inheritance, mutations, and narrative relationships.
"""

import asyncio
from typing import Set, Optional
from datetime import datetime

import pytest
from pydantic import BaseModel, Field

from goldentooth_agent.core.recursive_agents.spawning import (
    SpawnConfiguration,
    SpawnEngine,
    TraitInheritance,
    NarrativeRelationship,
    SpawnEvent,
    SpawnError,
    AgentMutation,
    PersonalityTrait,
)
from goldentooth_agent.core.recursive_agents.lifecycle import (
    AgentIdentity,
    AgentLifecycle,
)


class TestSpawnConfiguration:
    """Test spawn configuration and inheritance rules."""
    
    def test_default_spawn_configuration(self):
        """Test default spawn settings favor inheritance."""
        # When: Creating default spawn config
        config = SpawnConfiguration()
        
        # Then: Should have sensible defaults
        assert config.inherit_tools is True
        assert config.inherit_context is False  # Privacy by default
        assert config.inherit_objectives is False  # Fresh start
        assert config.mutation_rate == 0.1
        assert config.narrative_relationship == NarrativeRelationship.OFFSPRING
    
    def test_rivalry_spawn_configuration(self):
        """Test spawn configuration for creating rivals."""
        # When: Creating a rival
        config = SpawnConfiguration(
            inherit_tools=True,  # Same capabilities
            inherit_context=False,  # Different perspective
            inherit_objectives=False,  # Opposing goals
            mutation_rate=0.3,  # Higher variation
            narrative_relationship=NarrativeRelationship.RIVAL,
            personality_modifier="oppositional"
        )
        
        # Then: Configuration should reflect rivalry
        assert config.narrative_relationship == NarrativeRelationship.RIVAL
        assert config.personality_modifier == "oppositional"
        assert config.mutation_rate > 0.2  # Higher chance of difference
    
    def test_apprentice_spawn_configuration(self):
        """Test spawn configuration for mentor/apprentice relationship."""
        # When: Creating an apprentice
        config = SpawnConfiguration(
            inherit_tools=True,
            inherit_context=True,  # Learn from mentor
            inherit_objectives=True,  # Share goals initially
            mutation_rate=0.05,  # Slight variations
            narrative_relationship=NarrativeRelationship.APPRENTICE,
            skill_transfer_rate=0.7  # Partial skill transfer
        )
        
        # Then: Should facilitate learning relationship
        assert config.inherit_context is True
        assert config.skill_transfer_rate == 0.7
        assert config.mutation_rate < 0.1  # Faithful reproduction


class TestSpawnEngine:
    """Test the engine that creates new agents from existing ones."""
    
    @pytest.fixture
    def spawn_engine(self):
        """Create a spawn engine for testing."""
        return SpawnEngine()
    
    @pytest.fixture
    def parent_agent(self):
        """Create a parent agent for spawning tests."""
        return AgentIdentity(
            id="parent-001",
            name="Experienced Parent",
            creator_id=None,
            birth_time=datetime.utcnow(),
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=[],
            narrative_role="mentor",
            traits={
                PersonalityTrait.WISE,
                PersonalityTrait.PATIENT,
                PersonalityTrait.CAUTIOUS
            }
        )
    
    @pytest.mark.asyncio
    async def test_basic_offspring_spawning(self, spawn_engine, parent_agent):
        """Test creating a basic offspring agent."""
        # Given: A spawn configuration for offspring
        config = SpawnConfiguration(
            narrative_relationship=NarrativeRelationship.OFFSPRING,
            inherit_tools=True,
            mutation_rate=0.1
        )
        
        # When: Spawning a child
        spawn_event = await spawn_engine.spawn_agent(
            parent=parent_agent,
            config=config,
            name="First Child"
        )
        
        # Then: Child should be properly created
        child = spawn_event.spawned_agent
        assert child.creator_id == parent_agent.id
        assert parent_agent.id in child.lineage
        assert child.name == "First Child"
        assert spawn_event.relationship == NarrativeRelationship.OFFSPRING
    
    @pytest.mark.asyncio
    async def test_trait_inheritance_with_mutation(self, spawn_engine, parent_agent):
        """Test personality trait inheritance and mutation."""
        # Given: Parent with specific traits
        # When: Spawning multiple children to test mutation
        children = []
        for i in range(10):
            spawn_event = await spawn_engine.spawn_agent(
                parent=parent_agent,
                config=SpawnConfiguration(
                    mutation_rate=0.3,  # 30% chance of trait mutation
                    inherit_traits=True
                ),
                name=f"Child {i}"
            )
            children.append(spawn_event.spawned_agent)
        
        # Then: Some children should have mutated traits
        parent_traits = parent_agent.traits
        mutation_count = 0
        
        for child in children:
            if child.traits != parent_traits:
                mutation_count += 1
                # Mutations should be reasonable
                trait_diff = child.traits.symmetric_difference(parent_traits)
                assert len(trait_diff) <= 2  # Max 2 trait changes
        
        # With 30% mutation rate, expect some mutations
        assert mutation_count > 0
        assert mutation_count < 10  # But not all should mutate
    
    @pytest.mark.asyncio
    async def test_rival_creation_inverts_traits(self, spawn_engine, parent_agent):
        """Test that rivals have opposing personality traits."""
        # Given: A configuration for creating a rival
        config = SpawnConfiguration(
            narrative_relationship=NarrativeRelationship.RIVAL,
            personality_modifier="inverse",
            mutation_rate=0.0  # No random mutation
        )
        
        # When: Creating a rival
        spawn_event = await spawn_engine.spawn_agent(
            parent=parent_agent,
            config=config,
            name="Bitter Rival"
        )
        
        # Then: Rival should have opposing traits
        rival = spawn_event.spawned_agent
        assert PersonalityTrait.WISE in parent_agent.traits
        assert PersonalityTrait.FOOLISH in rival.traits
        
        assert PersonalityTrait.CAUTIOUS in parent_agent.traits
        assert PersonalityTrait.RECKLESS in rival.traits
    
    @pytest.mark.asyncio
    async def test_multi_generational_spawning(self, spawn_engine, parent_agent):
        """Test spawning through multiple generations."""
        # Given: An initial parent
        current_parent = parent_agent
        lineage_chain = [parent_agent.id]
        
        # When: Creating three generations
        for generation in range(3):
            spawn_event = await spawn_engine.spawn_agent(
                parent=current_parent,
                config=SpawnConfiguration(
                    narrative_relationship=NarrativeRelationship.OFFSPRING,
                    generational_degradation=0.1  # Skills weaken over time
                ),
                name=f"Generation {generation + 2}"
            )
            
            child = spawn_event.spawned_agent
            lineage_chain.append(child.id)
            current_parent = child
        
        # Then: Final descendant should have full lineage
        final_child = current_parent
        assert len(final_child.lineage) == 4  # 3 ancestors + original
        assert all(ancestor in final_child.lineage for ancestor in lineage_chain[:-1])
    
    @pytest.mark.asyncio
    async def test_clone_spawning_exact_copy(self, spawn_engine, parent_agent):
        """Test creating an exact clone of an agent."""
        # Given: Clone configuration
        config = SpawnConfiguration(
            narrative_relationship=NarrativeRelationship.CLONE,
            mutation_rate=0.0,
            inherit_tools=True,
            inherit_context=True,
            inherit_objectives=True,
            inherit_traits=True
        )
        
        # When: Creating a clone
        spawn_event = await spawn_engine.spawn_agent(
            parent=parent_agent,
            config=config,
            name="Perfect Clone"
        )
        
        # Then: Clone should be identical except for identity
        clone = spawn_event.spawned_agent
        assert clone.traits == parent_agent.traits
        assert clone.narrative_role == parent_agent.narrative_role
        assert clone.id != parent_agent.id  # But different identity
        assert spawn_event.is_perfect_clone is True
    
    @pytest.mark.asyncio
    async def test_spawn_with_narrative_purpose(self, spawn_engine, parent_agent):
        """Test spawning with specific narrative purpose."""
        # Given: Narrative-driven spawn configuration
        config = SpawnConfiguration(
            narrative_relationship=NarrativeRelationship.NEMESIS,
            narrative_purpose="avenge_fallen_master",
            inherit_objectives=False,
            mutation_rate=0.2
        )
        
        # When: Creating a nemesis
        spawn_event = await spawn_engine.spawn_agent(
            parent=parent_agent,
            config=config,
            name="Vengeful Student",
            initial_objective="destroy_creator"
        )
        
        # Then: Spawn should have narrative metadata
        nemesis = spawn_event.spawned_agent
        assert spawn_event.narrative_purpose == "avenge_fallen_master"
        assert spawn_event.initial_objective == "destroy_creator"
        assert nemesis.narrative_role == "nemesis"
    
    @pytest.mark.asyncio
    async def test_ephemeral_spawn_limitations(self, spawn_engine):
        """Test that ephemeral agents have spawn limitations."""
        # Given: An ephemeral parent
        ephemeral_parent = AgentIdentity(
            id="ephemeral-001",
            name="Temporary Being",
            creator_id=None,
            birth_time=datetime.utcnow(),
            lifecycle=AgentLifecycle.EPHEMERAL,
            lineage=[],
            narrative_role="messenger"
        )
        
        # When: Attempting to spawn from ephemeral
        with pytest.raises(SpawnError, match="Ephemeral agents cannot spawn"):
            await spawn_engine.spawn_agent(
                parent=ephemeral_parent,
                config=SpawnConfiguration(),
                name="Impossible Child"
            )
    
    @pytest.mark.asyncio
    async def test_spawn_resource_limits(self, spawn_engine, parent_agent):
        """Test resource limits on spawning."""
        # Given: Resource-limited configuration
        spawn_engine.set_resource_limits(
            max_children_per_agent=3,
            max_spawn_depth=2
        )
        
        # When: Spawning up to the limit
        children = []
        for i in range(3):
            spawn_event = await spawn_engine.spawn_agent(
                parent=parent_agent,
                config=SpawnConfiguration(),
                name=f"Child {i}"
            )
            children.append(spawn_event.spawned_agent)
        
        # Then: Further spawning should fail
        with pytest.raises(SpawnError, match="spawn limit"):
            await spawn_engine.spawn_agent(
                parent=parent_agent,
                config=SpawnConfiguration(),
                name="One Too Many"
            )
    
    @pytest.mark.asyncio
    async def test_concurrent_spawning_safety(self, spawn_engine, parent_agent):
        """Test that concurrent spawning maintains consistency."""
        # Given: Multiple spawn requests
        spawn_configs = [
            SpawnConfiguration(mutation_rate=0.1),
            SpawnConfiguration(mutation_rate=0.2),
            SpawnConfiguration(mutation_rate=0.3),
        ]
        
        # When: Spawning concurrently
        async def spawn_child(config, index):
            return await spawn_engine.spawn_agent(
                parent=parent_agent,
                config=config,
                name=f"Concurrent Child {index}"
            )
        
        spawn_events = await asyncio.gather(*[
            spawn_child(config, i) 
            for i, config in enumerate(spawn_configs)
        ])
        
        # Then: All children should be unique and valid
        child_ids = {event.spawned_agent.id for event in spawn_events}
        assert len(child_ids) == 3  # All unique IDs
        
        # All should have same parent
        for event in spawn_events:
            assert event.spawned_agent.creator_id == parent_agent.id


class TestNarrativeSpawning:
    """Test narrative-driven spawning scenarios."""
    
    @pytest.mark.asyncio
    async def test_betrayal_creates_nemesis(self, spawn_engine):
        """Test that betrayal can transform ally into nemesis."""
        # Given: A trusted ally
        ally = AgentIdentity(
            id="trusted-ally-001",
            name="Loyal Friend",
            creator_id="hero-001",
            birth_time=datetime.utcnow(),
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=["hero-001"],
            narrative_role="ally",
            traits={PersonalityTrait.LOYAL, PersonalityTrait.TRUSTING}
        )
        
        # When: Betrayal transforms them
        betrayal_event = await spawn_engine.transform_agent(
            agent=ally,
            transformation_type="betrayal",
            catalyst="discovered_dark_secret",
            new_relationship=NarrativeRelationship.NEMESIS
        )
        
        # Then: Should create nemesis version
        nemesis = betrayal_event.transformed_agent
        assert nemesis.narrative_role == "nemesis"
        assert PersonalityTrait.LOYAL not in nemesis.traits
        assert PersonalityTrait.VENGEFUL in nemesis.traits
        assert betrayal_event.transformation_catalyst == "discovered_dark_secret"
    
    @pytest.mark.asyncio
    async def test_faction_spawning(self, spawn_engine):
        """Test spawning multiple agents as a faction."""
        # Given: A faction leader
        leader = AgentIdentity(
            id="faction-leader-001",
            name="Charismatic Leader",
            creator_id=None,
            birth_time=datetime.utcnow(),
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=[],
            narrative_role="faction_leader",
            traits={PersonalityTrait.CHARISMATIC, PersonalityTrait.AMBITIOUS}
        )
        
        # When: Creating a faction
        faction_event = await spawn_engine.spawn_faction(
            leader=leader,
            faction_size=5,
            faction_type="rebel_alliance",
            hierarchy_type="democratic",
            shared_objective="overthrow_tyranny"
        )
        
        # Then: Should create cohesive faction
        assert len(faction_event.members) == 5
        assert all(m.creator_id == leader.id for m in faction_event.members)
        assert faction_event.faction_type == "rebel_alliance"
        assert faction_event.shared_objective == "overthrow_tyranny"
        
        # Members should have varied but compatible roles
        roles = {m.narrative_role for m in faction_event.members}
        assert "strategist" in roles or "advisor" in roles
        assert "warrior" in roles or "enforcer" in roles