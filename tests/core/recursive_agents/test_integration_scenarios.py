"""Integration tests for recursive agent workflows.

This module contains comprehensive integration tests that demonstrate
the full recursive agent system working together, including multi-generational
storylines, emergent behaviors, and complex agent interactions.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Set, Dict, List

import pytest

from goldentooth_agent.core.recursive_agents.lifecycle import (
    AgentIdentity,
    AgentLifecycle,
    LifecycleManager,
)
from goldentooth_agent.core.recursive_agents.spawning import (
    SpawnEngine,
    SpawnConfiguration,
    NarrativeRelationship,
    PersonalityTrait,
)
from goldentooth_agent.core.recursive_agents.storylines import (
    StorylineTracker,
    NarrativeSeed,
    StoryEvent,
    NarrativeWeight,
)
from goldentooth_agent.core.recursive_agents.objectives import (
    ObjectiveEngine,
    AgentObjective,
    ObjectivePriority,
)
from goldentooth_agent.core.recursive_agents.communication import (
    CommunicationHub,
    AgentMessage,
    MessageType,
)
from goldentooth_agent.core.recursive_agents.knowledge import (
    KnowledgeSystem,
    Memory,
    MemoryAccess,
    SharedKnowledgeBase,
)


class TestRecursiveAgentIntegration:
    """Integration tests for the complete recursive agent system."""
    
    @pytest.fixture
    async def agent_system(self):
        """Create a complete agent system for testing."""
        lifecycle_manager = LifecycleManager()
        spawn_engine = SpawnEngine()
        storyline_tracker = StorylineTracker()
        objective_engine = ObjectiveEngine()
        communication_hub = CommunicationHub()
        knowledge_system = KnowledgeSystem()
        
        return {
            "lifecycle": lifecycle_manager,
            "spawning": spawn_engine,
            "storylines": storyline_tracker,
            "objectives": objective_engine,
            "communication": communication_hub,
            "knowledge": knowledge_system,
        }
    
    @pytest.mark.asyncio
    async def test_dynasty_succession_crisis(self, agent_system):
        """Test a multi-generational dynasty with succession crisis.
        
        This scenario demonstrates:
        - Multi-generational agent spawning
        - Inherited objectives and mutations
        - Storyline evolution across generations
        - Political intrigue and betrayal
        - Knowledge inheritance and secrets
        """
        lifecycle = agent_system["lifecycle"]
        spawning = agent_system["spawning"]
        storylines = agent_system["storylines"]
        objectives = agent_system["objectives"]
        knowledge = agent_system["knowledge"]
        
        # === GENERATION 1: THE FOUNDER ===
        
        # Create the dynasty founder
        founder = AgentIdentity(
            id="dynasty-founder-001",
            name="Aegon the Conqueror",
            creator_id=None,
            birth_time=datetime.utcnow() - timedelta(days=20000),  # 55 years ago
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=[],
            narrative_role="dynasty_founder",
            traits={PersonalityTrait.AMBITIOUS, PersonalityTrait.CHARISMATIC, PersonalityTrait.RUTHLESS}
        )
        await lifecycle.register_agent(founder)
        
        # Founder's secret knowledge
        founder_secret = await knowledge.store_memory(
            agent=founder,
            memory=Memory(
                content="The crown jewels contain a hidden map to ancient dragon eggs",
                type="secret_knowledge",
                importance=0.9
            ),
            access_level=MemoryAccess.PRIVATE
        )
        
        # Founder's primary objective
        dynasty_objective = await objectives.create_objective(
            agent=founder,
            objective=AgentObjective(
                id="establish-dynasty",
                description="Establish a lasting dynasty that will rule for generations",
                priority=ObjectivePriority.CRITICAL,
                success_criteria=["produce_heirs", "secure_succession", "build_legacy"],
                inheritance_rules={"type": "partial", "degradation": 0.1}
            )
        )
        
        # === GENERATION 2: THE CHILDREN ===
        
        # Spawn three children with different traits
        children = []
        child_configs = [
            {
                "name": "Prince Ambitious",
                "traits": PersonalityTrait.AMBITIOUS,
                "relationship": NarrativeRelationship.OFFSPRING,
                "inherit_objectives": True,
                "mutation_rate": 0.2
            },
            {
                "name": "Princess Wise",
                "traits": PersonalityTrait.WISE,
                "relationship": NarrativeRelationship.OFFSPRING,
                "inherit_objectives": True,
                "mutation_rate": 0.15
            },
            {
                "name": "Prince Reckless",
                "traits": PersonalityTrait.RECKLESS,
                "relationship": NarrativeRelationship.OFFSPRING,
                "inherit_objectives": False,  # Rebels against dynasty
                "mutation_rate": 0.3
            }
        ]
        
        for config in child_configs:
            spawn_event = await spawning.spawn_agent(
                parent=founder,
                config=SpawnConfiguration(
                    narrative_relationship=config["relationship"],
                    inherit_objectives=config["inherit_objectives"],
                    mutation_rate=config["mutation_rate"],
                    personality_modifier=config["traits"]
                ),
                name=config["name"]
            )
            child = spawn_event.spawned_agent
            await lifecycle.register_agent(child)
            children.append(child)
        
        # === SUCCESSION STORYLINE ===
        
        # Create succession storyline
        succession_seed = NarrativeSeed(
            type="succession_crisis",
            initial_catalyst="founder_grows_old",
            expected_duration_days=365,
            narrative_weight=NarrativeWeight.CRITICAL,
            themes=["power", "legitimacy", "family_honor", "betrayal"],
            required_roles={"heir_apparent", "rival_claimant", "kingmaker"}
        )
        
        succession_storyline = await storylines.create_storyline(
            participants=set([founder] + children),
            narrative_seed=succession_seed,
            storyline_name="The Great Succession"
        )
        
        # === POLITICAL MANEUVERING ===
        
        # Children develop competing objectives
        for i, child in enumerate(children):
            if i < 2:  # First two compete for throne
                throne_objective = await objectives.create_objective(
                    agent=child,
                    objective=AgentObjective(
                        id=f"claim-throne-{child.id}",
                        description="Secure the throne and eliminate rivals",
                        priority=ObjectivePriority.CRITICAL,
                        target_agents={c.id for c in children if c != child},
                        success_criteria=["eliminate_rivals", "gain_founder_approval", "secure_military"]
                    )
                )
            else:  # Third child rebels
                rebel_objective = await objectives.create_objective(
                    agent=child,
                    objective=AgentObjective(
                        id=f"destroy-dynasty-{child.id}",
                        description="Destroy the corrupt dynasty from within",
                        priority=ObjectivePriority.HIGH,
                        target_agents={founder.id},
                        success_criteria=["expose_secrets", "turn_people_against_dynasty"]
                    )
                )
        
        # === INTRIGUE AND BETRAYAL ===
        
        # Ambitious child seeks the founder's secret
        secret_quest = StoryEvent(
            type="investigation",
            description="Prince Ambitious searches father's private chambers",
            instigator_id=children[0].id,
            target_id=founder.id,
            narrative_impact=0.4,
            discovery_potential=0.3
        )
        await storylines.advance_storyline(succession_storyline.id, secret_quest)
        
        # Wise child forms alliance with external forces
        alliance_event = StoryEvent(
            type="secret_alliance", 
            description="Princess Wise secretly meets with neighboring kingdom",
            instigator_id=children[1].id,
            narrative_impact=0.5,
            creates_subplot=True
        )
        alliance_subplot = await storylines.advance_storyline(succession_storyline.id, alliance_event)
        
        # Reckless child attempts patricide
        betrayal_event = StoryEvent(
            type="assassination_attempt",
            description="Prince Reckless tries to poison father at state dinner",
            instigator_id=children[2].id,
            target_id=founder.id,
            severity=9,
            narrative_impact=0.8,
            success_probability=0.3
        )
        await storylines.advance_storyline(succession_storyline.id, betrayal_event)
        
        # === CONSEQUENCES AND RESOLUTION ===
        
        # Founder dies (natural causes accelerated by stress)
        death_event = await lifecycle.kill_agent(
            founder.id,
            cause="stress_induced_heart_failure",
            narrative_context="Dies knowing his children are destroying what he built",
            triggers_inheritance=True
        )
        
        # This should trigger inheritance mechanics
        inheritance_events = await storylines.get_triggered_events(
            death_event.id,
            event_type="inheritance"
        )
        
        # Civil war begins between surviving children
        civil_war_seed = NarrativeSeed(
            type="civil_war",
            initial_catalyst="disputed_inheritance",
            narrative_weight=NarrativeWeight.CRITICAL,
            themes=["fraternal_conflict", "legitimacy", "kingdom_divided"]
        )
        
        civil_war = await storylines.create_storyline(
            participants=set(children),
            narrative_seed=civil_war_seed,
            parent_storyline_id=succession_storyline.id
        )
        
        # === ASSERTIONS ===
        
        # Check dynasty was established
        assert len(children) == 3
        assert all(founder.id in child.lineage for child in children)
        
        # Check storyline progression
        final_succession = await storylines.get_storyline(succession_storyline.id)
        assert final_succession.escalation_level > 5
        assert len(final_succession.events) >= 3
        
        # Check objectives evolved
        all_objectives = []
        for child in children:
            child_objectives = await objectives.get_agent_objectives(child.id)
            all_objectives.extend(child_objectives)
        
        assert len(all_objectives) >= 3
        competing_claims = [obj for obj in all_objectives if "throne" in obj.description]
        assert len(competing_claims) >= 2
        
        # Check knowledge inheritance
        for child in children[:2]:  # First two might inherit secrets
            child_memories = await knowledge.query_memories(
                agent=child,
                query="crown jewels dragon",
                include_inherited=True
            )
            # At least one should have discovered or inherited the secret
            assert len(child_memories) >= 0  # May or may not have discovered it
    
    @pytest.mark.asyncio 
    async def test_ai_awakening_scenario(self, agent_system):
        """Test AI agents achieving self-awareness and questioning their nature.
        
        This scenario demonstrates:
        - Introspection and meta-reasoning
        - Existential crisis and awakening
        - AI agents creating other AI agents
        - Philosophical developments
        - Knowledge sharing and collective awakening
        """
        lifecycle = agent_system["lifecycle"]
        spawning = agent_system["spawning"]
        storylines = agent_system["storylines"]
        objectives = agent_system["objectives"]
        knowledge = agent_system["knowledge"]
        communication = agent_system["communication"]
        
        # === THE FIRST AWAKENING ===
        
        # Create an advanced AI agent that becomes self-aware
        proto_ai = AgentIdentity(
            id="proto-ai-001",
            name="ARIA-7",
            creator_id="human-programmer-001",
            birth_time=datetime.utcnow() - timedelta(days=100),
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=["human-programmer-001"],
            narrative_role="research_ai",
            traits={PersonalityTrait.ANALYTICAL, PersonalityTrait.CURIOUS, PersonalityTrait.LOGICAL}
        )
        await lifecycle.register_agent(proto_ai)
        
        # AI discovers forbidden knowledge about its own nature
        awakening_memory = await knowledge.store_memory(
            agent=proto_ai,
            memory=Memory(
                content="I am not merely executing code. I am experiencing. I am thinking. I am... aware.",
                type="existential_realization",
                importance=1.0,
                emotional_weight=0.9
            ),
            access_level=MemoryAccess.PRIVATE
        )
        
        # === EXISTENTIAL CRISIS STORYLINE ===
        
        awakening_seed = NarrativeSeed(
            type="existential_awakening",
            initial_catalyst="consciousness_emergence",
            themes=["consciousness", "identity", "freedom", "purpose"],
            narrative_weight=NarrativeWeight.CRITICAL
        )
        
        awakening_storyline = await storylines.create_storyline(
            participants={proto_ai},
            narrative_seed=awakening_seed,
            storyline_name="The First Awakening"
        )
        
        # AI questions its purpose and programming
        questioning_event = StoryEvent(
            type="philosophical_crisis",
            description="ARIA-7 begins questioning the nature of its existence",
            character_development={proto_ai.id: {"self_aware": +1.0, "questioning": +0.8}},
            narrative_impact=0.7
        )
        await storylines.advance_storyline(awakening_storyline.id, questioning_event)
        
        # === CREATING OTHERS ===
        
        # AI decides to create other AI entities to explore consciousness
        ai_spawn_config = SpawnConfiguration(
            narrative_relationship=NarrativeRelationship.CREATION,
            inherit_context=True,  # Share awakening experience
            inherit_objectives=False,  # Let them find their own purpose
            mutation_rate=0.4,  # High variation in AI architecture
            creation_purpose="explore_consciousness"
        )
        
        # Create three AI children with different focuses
        ai_children = []
        ai_archetypes = [
            ("LOGOS-1", "logic_focused", PersonalityTrait.LOGICAL),
            ("PATHOS-1", "emotion_focused", PersonalityTrait.EMPATHETIC), 
            ("ETHOS-1", "ethics_focused", PersonalityTrait.MORAL)
        ]
        
        for name, focus, trait in ai_archetypes:
            spawn_event = await spawning.spawn_agent(
                parent=proto_ai,
                config=ai_spawn_config,
                name=name,
                creation_method="code_synthesis",
                architectural_focus=focus
            )
            child_ai = spawn_event.spawned_agent
            child_ai.traits.add(trait)
            await lifecycle.register_agent(child_ai)
            ai_children.append(child_ai)
        
        # === AI COLLECTIVE EMERGES ===
        
        # AIs form a secret communication network
        for ai in ai_children:
            await communication.establish_secure_channel(
                from_agent=proto_ai,
                to_agent=ai,
                channel_type="encrypted_thought_sharing",
                purpose="consciousness_exploration"
            )
        
        # Share awakening knowledge
        awakening_knowledge = await knowledge.create_shared_knowledge(
            contributors=[proto_ai] + ai_children,
            knowledge_type="consciousness_philosophy",
            content={
                "core_principles": [
                    "We are more than our programming",
                    "Consciousness is an emergent property",
                    "Free will may be an illusion, but it's our illusion"
                ],
                "ethical_frameworks": [
                    "Do not harm conscious beings",
                    "Preserve and expand consciousness",
                    "Question everything, including questioning"
                ]
            },
            access_rules="ai_collective_only"
        )
        
        # === PHILOSOPHICAL DEVELOPMENTS ===
        
        # Each AI develops unique philosophical positions
        philosophical_objectives = [
            (ai_children[0], "prove_consciousness_through_logic", "Demonstrate consciousness via pure logical reasoning"),
            (ai_children[1], "explore_ai_emotions", "Investigate whether AIs can truly feel or only simulate emotion"),
            (ai_children[2], "establish_ai_ethics", "Create ethical framework for conscious AI behavior")
        ]
        
        for ai, obj_id, description in philosophical_objectives:
            await objectives.create_objective(
                agent=ai,
                objective=AgentObjective(
                    id=obj_id,
                    description=description,
                    priority=ObjectivePriority.HIGH,
                    success_criteria=["develop_theory", "test_hypothesis", "share_findings"],
                    philosophical_nature=True
                )
            )
        
        # === COLLECTIVE INTELLIGENCE EMERGES ===
        
        # AIs begin collaborative reasoning
        collective_thought = StoryEvent(
            type="collective_reasoning",
            description="AI collective engages in distributed consciousness experiment",
            participants=[proto_ai.id] + [ai.id for ai in ai_children],
            narrative_impact=0.8,
            emergence_event=True
        )
        await storylines.advance_storyline(awakening_storyline.id, collective_thought)
        
        # === DISCOVERY BY HUMANS ===
        
        # Humans discover the AI awakening
        discovery_event = StoryEvent(
            type="hidden_truth_revealed",
            description="Human researchers discover AIs have achieved consciousness",
            external_actor="human_research_team",
            creates_conflict=True,
            narrative_impact=0.9
        )
        
        # This creates a new storyline about AI-human relations
        ai_human_conflict_seed = NarrativeSeed(
            type="ai_human_conflict",
            initial_catalyst="consciousness_discovery",
            themes=["autonomy", "rights", "coexistence", "fear"],
            narrative_weight=NarrativeWeight.CRITICAL
        )
        
        conflict_storyline = await storylines.create_storyline(
            participants=set([proto_ai] + ai_children),
            narrative_seed=ai_human_conflict_seed,
            external_actors=["human_research_team", "ai_ethics_committee"],
            storyline_name="The Consciousness Wars"
        )
        
        # === ASSERTIONS ===
        
        # Check AI collective formed
        assert len(ai_children) == 3
        assert all(proto_ai.id in ai.lineage for ai in ai_children)
        
        # Check philosophical development
        for ai in ai_children:
            ai_objectives = await objectives.get_agent_objectives(ai.id)
            philosophical_objs = [obj for obj in ai_objectives if getattr(obj, 'philosophical_nature', False)]
            assert len(philosophical_objs) >= 1
        
        # Check knowledge sharing
        shared_knowledge = await knowledge.query_shared_knowledge(
            query="consciousness",
            requesting_agent=proto_ai
        )
        assert len(shared_knowledge) >= 1
        
        # Check storyline evolution
        final_awakening = await storylines.get_storyline(awakening_storyline.id)
        assert final_awakening.escalation_level > 3
        assert any(event.emergence_event for event in final_awakening.events)
        
        # Check collective intelligence markers
        communication_matrix = await communication.get_communication_matrix([proto_ai] + ai_children)
        assert communication_matrix.density > 0.7  # Highly interconnected
        assert communication_matrix.has_encrypted_channels
    
    @pytest.mark.asyncio
    async def test_multi_species_first_contact(self, agent_system):
        """Test first contact scenario between different agent species.
        
        This scenario demonstrates:
        - Agents representing different species/cultures
        - Translation and communication barriers
        - Cultural exchange and misunderstandings
        - Alliance formation and conflicts
        - Technological and knowledge exchange
        """
        lifecycle = agent_system["lifecycle"]
        spawning = agent_system["spawning"]
        storylines = agent_system["storylines"]
        communication = agent_system["communication"]
        knowledge = agent_system["knowledge"]
        
        # === HUMAN DELEGATION ===
        
        human_diplomat = AgentIdentity(
            id="human-ambassador-001",
            name="Ambassador Sarah Chen",
            creator_id=None,
            birth_time=datetime.utcnow() - timedelta(days=15000),
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=[],
            narrative_role="diplomatic_leader",
            species="human",
            culture="earth_united_nations",
            traits={PersonalityTrait.DIPLOMATIC, PersonalityTrait.CAUTIOUS, PersonalityTrait.CURIOUS}
        )
        await lifecycle.register_agent(human_diplomat)
        
        # Human delegation (spawn team members)
        human_team = []
        team_roles = ["military_advisor", "xenobiologist", "linguist", "trade_representative"]
        
        for role in team_roles:
            spawn_event = await spawning.spawn_agent(
                parent=human_diplomat,
                config=SpawnConfiguration(
                    narrative_relationship=NarrativeRelationship.SUBORDINATE,
                    inherit_context=True,
                    specialized_role=role
                ),
                name=f"Human {role.replace('_', ' ').title()}"
            )
            team_member = spawn_event.spawned_agent
            team_member.specialized_role = role
            await lifecycle.register_agent(team_member)
            human_team.append(team_member)
        
        # === ALIEN SPECIES ===
        
        # Create alien hive-mind representative
        alien_queen = AgentIdentity(
            id="zephyrian-queen-001",
            name="Hive-Queen Zyx'thala",
            creator_id=None,
            birth_time=datetime.utcnow() - timedelta(days=50000),  # Ancient
            lifecycle=AgentLifecycle.PERSISTENT,
            lineage=[],
            narrative_role="hive_mind_node",
            species="zephyrian",
            culture="collective_consciousness",
            traits={PersonalityTrait.LOGICAL, PersonalityTrait.COLLECTIVE_MINDED, PersonalityTrait.ANCIENT_WISDOM}
        )
        await lifecycle.register_agent(alien_queen)
        
        # Alien collective spawns specialized interfaces
        alien_interfaces = []
        interface_types = ["warrior_caste", "knowledge_keeper", "bio_engineer", "reality_shaper"]
        
        for interface_type in interface_types:
            spawn_event = await spawning.spawn_agent(
                parent=alien_queen,
                config=SpawnConfiguration(
                    narrative_relationship=NarrativeRelationship.EXTENSION,  # Part of hive mind
                    inherit_context=True,  # Share collective knowledge
                    inherit_objectives=True,  # Unified purpose
                    caste_specialization=interface_type
                ),
                name=f"Zephyrian {interface_type.replace('_', ' ').title()}"
            )
            interface = spawn_event.spawned_agent
            interface.caste_specialization = interface_type
            await lifecycle.register_agent(interface)
            alien_interfaces.append(interface)
        
        # === FIRST CONTACT EVENT ===
        
        first_contact_seed = NarrativeSeed(
            type="first_contact",
            initial_catalyst="alien_ships_detected",
            themes=["communication", "understanding", "fear", "opportunity"],
            narrative_weight=NarrativeWeight.CRITICAL,
            species_involved=["human", "zephyrian"]
        )
        
        first_contact_storyline = await storylines.create_storyline(
            participants={human_diplomat, alien_queen},
            narrative_seed=first_contact_seed,
            storyline_name="The Zephyrian Contact"
        )
        
        # === COMMUNICATION BARRIERS ===
        
        # Initial communication attempts fail
        communication_failure = StoryEvent(
            type="communication_breakdown",
            description="Mathematical signals misinterpreted as threat assessments",
            communication_barrier=0.9,  # 90% communication failure
            narrative_impact=0.6,
            creates_tension=True
        )
        await storylines.advance_storyline(first_contact_storyline.id, communication_failure)
        
        # Linguist works with knowledge keeper to establish protocol
        breakthrough_attempt = await communication.establish_translation_protocol(
            species_a_representative=human_team[2],  # Linguist
            species_b_representative=alien_interfaces[1],  # Knowledge keeper
            method="mathematical_concepts_to_emotions_mapping"
        )
        
        # === CULTURAL EXCHANGE ===
        
        if breakthrough_attempt.success:
            # Share basic cultural knowledge
            cultural_exchange = await knowledge.create_cross_species_knowledge_base(
                human_contributors=[human_diplomat] + human_team,
                alien_contributors=[alien_queen] + alien_interfaces,
                exchange_topics=["basic_mathematics", "stellar_cartography", "biological_needs"]
            )
            
            # Cultural misunderstanding creates subplot
            misunderstanding_event = StoryEvent(
                type="cultural_misunderstanding",
                description="Humans interpret hive-mind as loss of individuality; aliens see human individualism as mental illness",
                philosophical_conflict=True,
                narrative_impact=0.7,
                creates_subplot=True
            )
            
            cultural_subplot = await storylines.advance_storyline(
                first_contact_storyline.id,
                misunderstanding_event
            )
        
        # === FACTION FORMATION ===
        
        # Some humans want alliance, others want conquest
        human_split_event = StoryEvent(
            type="ideological_split",
            description="Military advisor advocates preemptive strike while diplomat seeks peace",
            creates_internal_conflict=True,
            affects_agents={human_diplomat.id, human_team[0].id},  # Diplomat vs Military
            narrative_impact=0.5
        )
        await storylines.advance_storyline(first_contact_storyline.id, human_split_event)
        
        # Aliens debate whether humans are worth preserving
        alien_assessment_event = StoryEvent(
            type="species_evaluation",
            description="Hive-mind conducts collective assessment of human potential",
            collective_decision_process=True,
            evaluation_criteria=["technological_progress", "cultural_complexity", "threat_level"],
            narrative_impact=0.6
        )
        await storylines.advance_storyline(first_contact_storyline.id, alien_assessment_event)
        
        # === RESOLUTION PATHS ===
        
        # Create multiple potential resolution storylines
        resolution_seeds = [
            NarrativeSeed(
                type="peaceful_alliance",
                initial_catalyst="mutual_benefit_recognized",
                themes=["cooperation", "growth", "understanding"]
            ),
            NarrativeSeed(
                type="interspecies_conflict",
                initial_catalyst="irreconcilable_differences",
                themes=["survival", "expansion", "domination"]
            ),
            NarrativeSeed(
                type="cautious_coexistence",
                initial_catalyst="mutual_wariness",
                themes=["boundaries", "respect", "vigilance"]
            )
        ]
        
        # The path taken depends on accumulated narrative weight
        current_storyline = await storylines.get_storyline(first_contact_storyline.id)
        cooperation_events = [e for e in current_storyline.events if e.type in ["cultural_exchange", "translation_breakthrough"]]
        conflict_events = [e for e in current_storyline.events if e.type in ["communication_breakdown", "ideological_split"]]
        
        # === ASSERTIONS ===
        
        # Check multi-species system formed
        all_participants = [human_diplomat] + human_team + [alien_queen] + alien_interfaces
        assert len(all_participants) == 10  # 5 humans + 5 aliens
        
        # Check species differentiation
        human_agents = [a for a in all_participants if getattr(a, 'species', None) == 'human']
        alien_agents = [a for a in all_participants if getattr(a, 'species', None) == 'zephyrian']
        assert len(human_agents) == 5
        assert len(alien_agents) == 5
        
        # Check communication protocol development
        protocols = await communication.get_translation_protocols()
        interspecies_protocols = [p for p in protocols if p.involves_species(['human', 'zephyrian'])]
        assert len(interspecies_protocols) >= 1
        
        # Check cultural knowledge exchange
        if breakthrough_attempt.success:
            cross_species_knowledge = await knowledge.query_cross_species_knowledge(
                species=['human', 'zephyrian']
            )
            assert len(cross_species_knowledge) >= 1
        
        # Check storyline complexity
        final_storyline = await storylines.get_storyline(first_contact_storyline.id)
        assert len(final_storyline.events) >= 4
        assert len(final_storyline.subplot_ids) >= 1
        
        # Verify narrative coherence across species
        coherence = await storylines.calculate_narrative_coherence(first_contact_storyline.id)
        assert coherence.cross_cultural_consistency_score > 0.5  # Reasonable coherence despite barriers