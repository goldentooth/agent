"""Test-driven development for agent storylines and narratives.

This module tests the storyline tracking system that manages ongoing
narratives between agents, including multi-agent interactions and
emergent plot developments.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Set, List, Optional
from enum import Enum

import pytest
from pydantic import BaseModel, Field

from goldentooth_agent.core.recursive_agents.storylines import (
    Storyline,
    StorylineTracker,
    NarrativeSeed,
    StoryEvent,
    StoryArc,
    PlotPoint,
    NarrativeWeight,
    StorylineError,
    CharacterRole,
    PlotTwist,
    NarrativeCoherence,
)
from goldentooth_agent.core.recursive_agents.lifecycle import (
    AgentIdentity,
    AgentLifecycle,
)


class TestNarrativeSeed:
    """Test narrative seeds that start storylines."""
    
    def test_power_struggle_seed(self):
        """Test creating a power struggle narrative seed."""
        # When: Creating a power struggle seed
        seed = NarrativeSeed(
            type="power_struggle",
            initial_catalyst="king_dies_without_heir",
            expected_duration_days=90,
            narrative_weight=NarrativeWeight.HIGH,
            themes=["succession", "legitimacy", "civil_war"],
            required_roles={"pretender", "kingmaker", "rebel_leader"}
        )
        
        # Then: Seed should define story parameters
        assert seed.type == "power_struggle"
        assert seed.initial_catalyst == "king_dies_without_heir"
        assert "succession" in seed.themes
        assert "pretender" in seed.required_roles
        assert seed.narrative_weight == NarrativeWeight.HIGH
    
    def test_romance_arc_seed(self):
        """Test creating a romance narrative seed."""
        # When: Creating romance seed
        seed = NarrativeSeed(
            type="star_crossed_lovers",
            initial_catalyst="enemies_meet_at_ball",
            expected_duration_days=60,
            narrative_weight=NarrativeWeight.MEDIUM,
            themes=["forbidden_love", "family_honor", "sacrifice"],
            required_roles={"lover", "rival", "disapproving_parent"},
            story_beats=[
                "meet_cute",
                "growing_attraction",
                "discovery_of_identity",
                "family_opposition",
                "tragic_climax"
            ]
        )
        
        # Then: Should have romance-specific structure
        assert "forbidden_love" in seed.themes
        assert "meet_cute" in seed.story_beats
        assert len(seed.story_beats) == 5  # Classic 5-act structure


class TestStorylineTracker:
    """Test the storyline tracker that manages narrative progression."""
    
    @pytest.fixture
    def storyline_tracker(self):
        """Create a storyline tracker for testing."""
        return StorylineTracker()
    
    @pytest.fixture
    def faction_agents(self):
        """Create agents for faction-based storylines."""
        return {
            "montague": AgentIdentity(
                id="montague-patriarch",
                name="Lord Montague",
                creator_id=None,
                birth_time=datetime.utcnow() - timedelta(days=5000),
                lifecycle=AgentLifecycle.PERSISTENT,
                lineage=[],
                narrative_role="family_patriarch"
            ),
            "capulet": AgentIdentity(
                id="capulet-patriarch", 
                name="Lord Capulet",
                creator_id=None,
                birth_time=datetime.utcnow() - timedelta(days=5000),
                lifecycle=AgentLifecycle.PERSISTENT,
                lineage=[],
                narrative_role="family_patriarch"
            ),
            "romeo": AgentIdentity(
                id="romeo-montague",
                name="Romeo Montague",
                creator_id="montague-patriarch",
                birth_time=datetime.utcnow() - timedelta(days=1000),
                lifecycle=AgentLifecycle.PERSISTENT,
                lineage=["montague-patriarch"],
                narrative_role="young_lover"
            ),
            "juliet": AgentIdentity(
                id="juliet-capulet",
                name="Juliet Capulet", 
                creator_id="capulet-patriarch",
                birth_time=datetime.utcnow() - timedelta(days=900),
                lifecycle=AgentLifecycle.PERSISTENT,
                lineage=["capulet-patriarch"],
                narrative_role="young_lover"
            )
        }
    
    @pytest.mark.asyncio
    async def test_create_feuding_families_storyline(self, storyline_tracker, faction_agents):
        """Test creating a multi-generational family feud."""
        # Given: Two patriarchs
        montague = faction_agents["montague"]
        capulet = faction_agents["capulet"]
        
        # When: Creating a feud storyline
        seed = NarrativeSeed(
            type="blood_feud",
            initial_catalyst="disputed_land_claim",
            expected_duration_days=365 * 10,  # 10 year feud
            narrative_weight=NarrativeWeight.HIGH,
            themes=["honor", "vengeance", "generational_conflict"]
        )
        
        storyline = await storyline_tracker.create_storyline(
            participants={montague, capulet},
            narrative_seed=seed,
            storyline_name="The Ancient Feud"
        )
        
        # Then: Storyline should be properly initialized
        assert storyline.name == "The Ancient Feud"
        assert storyline.type == "blood_feud"
        assert len(storyline.participants) == 2
        assert montague.id in storyline.participant_ids
        assert capulet.id in storyline.participant_ids
        assert storyline.status == "active"
    
    @pytest.mark.asyncio
    async def test_advance_storyline_with_events(self, storyline_tracker, faction_agents):
        """Test advancing storyline through story events."""
        # Given: An existing feud
        seed = NarrativeSeed(
            type="blood_feud",
            initial_catalyst="disputed_land_claim"
        )
        storyline = await storyline_tracker.create_storyline(
            participants={faction_agents["montague"], faction_agents["capulet"]},
            narrative_seed=seed
        )
        
        # When: Adding escalating events
        events = [
            StoryEvent(
                type="property_damage",
                description="Montagues burn Capulet vineyard",
                instigator_id="montague-patriarch",
                target_id="capulet-patriarch",
                severity=3,
                narrative_impact=0.3
            ),
            StoryEvent(
                type="personal_insult",
                description="Capulet calls Montague lineage illegitimate",
                instigator_id="capulet-patriarch",
                target_id="montague-patriarch",
                severity=5,
                narrative_impact=0.5
            ),
            StoryEvent(
                type="violence",
                description="Street brawl between family retainers",
                instigator_id="montague-retainer",
                target_id="capulet-retainer",
                severity=7,
                narrative_impact=0.7
            )
        ]
        
        for event in events:
            await storyline_tracker.advance_storyline(storyline.id, event)
        
        # Then: Storyline should escalate
        updated_storyline = await storyline_tracker.get_storyline(storyline.id)
        assert updated_storyline.escalation_level > storyline.escalation_level
        assert len(updated_storyline.events) == 3
        assert updated_storyline.events[-1].severity == 7  # Most recent is most severe
    
    @pytest.mark.asyncio
    async def test_romance_subplot_emerges(self, storyline_tracker, faction_agents):
        """Test that romance subplot can emerge from existing feud."""
        # Given: An existing family feud
        feud_seed = NarrativeSeed(type="blood_feud", initial_catalyst="ancient_grudge")
        feud = await storyline_tracker.create_storyline(
            participants={faction_agents["montague"], faction_agents["capulet"]},
            narrative_seed=feud_seed
        )
        
        # When: Young lovers meet
        romeo = faction_agents["romeo"]
        juliet = faction_agents["juliet"]
        
        romance_event = StoryEvent(
            type="secret_meeting",
            description="Star-crossed lovers meet at masquerade ball",
            instigator_id=romeo.id,
            target_id=juliet.id,
            narrative_impact=0.8,
            creates_subplot=True
        )
        
        # This should spawn a subplot
        subplot = await storyline_tracker.advance_storyline(feud.id, romance_event)
        
        # Then: Should create romance subplot linked to main feud
        assert subplot is not None
        assert subplot.type == "star_crossed_lovers"
        assert subplot.parent_storyline_id == feud.id
        assert romeo.id in subplot.participant_ids
        assert juliet.id in subplot.participant_ids
        
        # And: Main storyline should reference subplot
        updated_feud = await storyline_tracker.get_storyline(feud.id)
        assert subplot.id in updated_feud.subplot_ids
    
    @pytest.mark.asyncio
    async def test_plot_twist_changes_alliances(self, storyline_tracker, faction_agents):
        """Test that plot twists can dramatically alter storylines."""
        # Given: A power struggle between factions
        seed = NarrativeSeed(
            type="succession_crisis",
            initial_catalyst="king_dies_mysteriously"
        )
        
        # Add a third faction
        faction_agents["neutral"] = AgentIdentity(
            id="neutral-lord",
            name="Lord Neutral",
            creator_id=None,
            birth_time=datetime.utcnow() - timedelta(days=4000),
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=[],
            narrative_role="kingmaker"
        )
        
        storyline = await storyline_tracker.create_storyline(
            participants=set(faction_agents.values()),
            narrative_seed=seed
        )
        
        # When: Major plot twist occurs
        twist = PlotTwist(
            type="secret_revealed",
            description="Neutral lord is revealed as the late king's bastard son",
            revelation="neutral lord has legitimate claim to throne",
            affects_agents={faction_agents["neutral"].id},
            narrative_weight=NarrativeWeight.CRITICAL,
            changes_relationships=True
        )
        
        twist_event = await storyline_tracker.apply_plot_twist(storyline.id, twist)
        
        # Then: Should dramatically change storyline dynamics
        updated_storyline = await storyline_tracker.get_storyline(storyline.id)
        assert twist_event.narrative_impact > 0.8
        assert faction_agents["neutral"].id in updated_storyline.power_dynamics["claimants"]
        
        # Other factions should now see neutral as threat, not ally
        relationships = await storyline_tracker.get_relationship_matrix(storyline.id)
        neutral_id = faction_agents["neutral"].id
        assert relationships[faction_agents["montague"].id][neutral_id] == "rival"
        assert relationships[faction_agents["capulet"].id][neutral_id] == "rival"
    
    @pytest.mark.asyncio
    async def test_storyline_convergence(self, storyline_tracker, faction_agents):
        """Test multiple storylines converging into epic climax."""
        # Given: Multiple parallel storylines
        
        # 1. Family feud
        feud = await storyline_tracker.create_storyline(
            participants={faction_agents["montague"], faction_agents["capulet"]},
            narrative_seed=NarrativeSeed(type="blood_feud", initial_catalyst="ancient_grudge")
        )
        
        # 2. Romance subplot
        romance = await storyline_tracker.create_storyline(
            participants={faction_agents["romeo"], faction_agents["juliet"]},
            narrative_seed=NarrativeSeed(type="star_crossed_lovers", initial_catalyst="forbidden_attraction")
        )
        
        # 3. Political intrigue
        politics = await storyline_tracker.create_storyline(
            participants={faction_agents["montague"], faction_agents["capulet"], faction_agents["neutral"]},
            narrative_seed=NarrativeSeed(type="political_alliance", initial_catalyst="external_threat")
        )
        
        # When: Convergence event affects all storylines
        convergence_event = StoryEvent(
            type="tragic_death",
            description="Romeo dies defending Juliet from Capulet assassin",
            instigator_id="capulet-assassin",
            target_id=faction_agents["romeo"].id,
            affects_storylines={feud.id, romance.id, politics.id},
            narrative_impact=0.9,
            climax_event=True
        )
        
        convergence = await storyline_tracker.converge_storylines(
            storyline_ids={feud.id, romance.id, politics.id},
            convergence_event=convergence_event
        )
        
        # Then: Should create epic convergent storyline
        assert convergence.type == "epic_convergence"
        assert len(convergence.merged_storylines) == 3
        assert convergence.climax_event.target_id == faction_agents["romeo"].id
        
        # Original storylines should be marked as converged
        for storyline_id in {feud.id, romance.id, politics.id}:
            original = await storyline_tracker.get_storyline(storyline_id)
            assert original.status == "converged"
            assert original.convergence_id == convergence.id
    
    @pytest.mark.asyncio
    async def test_narrative_coherence_tracking(self, storyline_tracker, faction_agents):
        """Test that storylines maintain narrative coherence."""
        # Given: A storyline with character development
        storyline = await storyline_tracker.create_storyline(
            participants={faction_agents["romeo"]},
            narrative_seed=NarrativeSeed(
                type="coming_of_age",
                initial_catalyst="first_combat"
            )
        )
        
        # When: Adding character development events
        events = [
            StoryEvent(
                type="moral_choice",
                description="Romeo spares defeated enemy",
                character_development={"romeo": {"compassionate": +0.3, "honorable": +0.2}}
            ),
            StoryEvent(
                type="betrayal_by_friend", 
                description="Trusted friend sells Romeo's secrets",
                character_development={"romeo": {"trusting": -0.4, "cynical": +0.3}}
            ),
            StoryEvent(
                type="redemption_arc",
                description="Romeo forgives betrayer and gains wisdom",
                character_development={"romeo": {"wise": +0.5, "forgiving": +0.4}}
            )
        ]
        
        for event in events:
            await storyline_tracker.advance_storyline(storyline.id, event)
        
        # Then: Should track coherent character arc
        coherence = await storyline_tracker.calculate_narrative_coherence(storyline.id)
        
        assert coherence.character_consistency_score > 0.7
        assert coherence.plot_progression_score > 0.7
        assert coherence.thematic_unity_score > 0.7
        
        # Character should show meaningful development
        romeo_arc = coherence.character_arcs[faction_agents["romeo"].id]
        assert romeo_arc.growth_trajectory == "hero_journey"
        assert romeo_arc.final_state["wise"] > romeo_arc.initial_state.get("wise", 0)
    
    @pytest.mark.asyncio
    async def test_multi_agent_conspiracy(self, storyline_tracker):
        """Test complex multi-agent conspiracy storyline."""
        # Given: A conspiracy involving multiple agents
        conspirators = []
        for i in range(5):
            agent = AgentIdentity(
                id=f"conspirator-{i:03d}",
                name=f"Conspirator {i}",
                creator_id=None,
                birth_time=datetime.utcnow() - timedelta(days=2000),
                lifecycle=AgentLifecycle.PERSISTENT,
                lineage=[],
                narrative_role="conspirator"
            )
            conspirators.append(agent)
        
        # When: Creating conspiracy storyline
        conspiracy = await storyline_tracker.create_storyline(
            participants=set(conspirators),
            narrative_seed=NarrativeSeed(
                type="political_conspiracy",
                initial_catalyst="corrupt_ruler_seizes_power",
                themes=["justice", "sacrifice", "brotherhood"],
                required_roles={"mastermind", "inside_man", "muscle", "face", "money"}
            )
        )
        
        # And: Assigning specialized roles
        role_assignments = {
            conspirators[0].id: "mastermind",
            conspirators[1].id: "inside_man", 
            conspirators[2].id: "muscle",
            conspirators[3].id: "face",
            conspirators[4].id: "money"
        }
        
        await storyline_tracker.assign_roles(conspiracy.id, role_assignments)
        
        # Then: Should create complex web of relationships
        network = await storyline_tracker.analyze_conspiracy_network(conspiracy.id)
        
        assert network.central_figure_id == conspirators[0].id  # Mastermind
        assert len(network.trust_relationships) >= 5  # All pairs know each other
        assert network.secrecy_level > 0.8  # High secrecy
        assert network.betrayal_risk < 0.3  # Low initial betrayal risk
    
    @pytest.mark.asyncio
    async def test_storyline_dormancy_and_revival(self, storyline_tracker, faction_agents):
        """Test storylines going dormant and being revived."""
        # Given: An active storyline
        storyline = await storyline_tracker.create_storyline(
            participants={faction_agents["montague"], faction_agents["capulet"]},
            narrative_seed=NarrativeSeed(type="trade_dispute", initial_catalyst="broken_contract")
        )
        
        # When: Storyline goes dormant due to inactivity
        await storyline_tracker.advance_time(days=180)  # 6 months
        await storyline_tracker.check_storyline_health()
        
        updated = await storyline_tracker.get_storyline(storyline.id)
        assert updated.status == "dormant"
        
        # When: New event revives storyline
        revival_event = StoryEvent(
            type="old_wounds_reopened",
            description="Capulet heir discovers grandfather's hidden journal detailing Montague treachery",
            revival_catalyst=True,
            narrative_impact=0.6
        )
        
        await storyline_tracker.advance_storyline(storyline.id, revival_event)
        
        # Then: Storyline should be active again
        revived = await storyline_tracker.get_storyline(storyline.id)
        assert revived.status == "active"
        assert revived.dormancy_periods == 1
        assert len(revived.revival_events) == 1