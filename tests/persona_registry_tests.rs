use chrono::Utc;
use goldentooth_agent::core::{PersonaMetadata, PersonaRegistry, PersonaState};
use goldentooth_agent::error::{AgentError, PersonaId};

#[tokio::test]
async fn persona_registry_can_be_created() {
    let registry = PersonaRegistry::new();
    assert_eq!(registry.count().unwrap(), 0);
    assert!(registry.is_empty().unwrap());
}

#[tokio::test]
async fn persona_registry_can_register_persona() {
    let registry = PersonaRegistry::new();
    let persona_id = PersonaId::new(1);
    let metadata = PersonaMetadata {
        name: "Madam Calliope Harkthorn".to_string(),
        archetype: "AuthoritativeScholar".to_string(),
        service_domain: Some("ControlPlane".to_string()),
        created_at: Utc::now(),
        last_active: Utc::now(),
        state: PersonaState::Inactive,
    };

    let result = registry.register(persona_id, metadata.clone());
    assert!(result.is_ok());
    assert_eq!(registry.count().unwrap(), 1);
    assert!(registry.contains(persona_id).unwrap());
}

#[tokio::test]
async fn persona_registry_prevents_duplicate_registration() {
    let registry = PersonaRegistry::new();
    let persona_id = PersonaId::new(1);
    let metadata = PersonaMetadata {
        name: "Dr. Caudex Thorne".to_string(),
        archetype: "ClinicalAnalyst".to_string(),
        service_domain: Some("Monitoring".to_string()),
        created_at: Utc::now(),
        last_active: Utc::now(),
        state: PersonaState::Inactive,
    };

    // First registration should succeed
    let result1 = registry.register(persona_id, metadata.clone());
    assert!(result1.is_ok());

    // Second registration should fail
    let result2 = registry.register(persona_id, metadata);
    assert!(result2.is_err());

    match result2.unwrap_err() {
        AgentError::PersonaAlreadyExists(id) => assert_eq!(id, persona_id),
        _ => panic!("Expected PersonaAlreadyExists error"),
    }

    assert_eq!(registry.count().unwrap(), 1);
}

#[tokio::test]
async fn persona_registry_can_retrieve_by_id() {
    let registry = PersonaRegistry::new();
    let persona_id = PersonaId::new(1);
    let metadata = PersonaMetadata {
        name: "Miss Glestrine Vellum".to_string(),
        archetype: "WittySkeptic".to_string(),
        service_domain: Some("TrafficManagement".to_string()),
        created_at: Utc::now(),
        last_active: Utc::now(),
        state: PersonaState::Active,
    };

    registry.register(persona_id, metadata.clone()).unwrap();

    let retrieved = registry.get(persona_id).unwrap();
    assert!(retrieved.is_some());

    let retrieved_metadata = retrieved.unwrap();
    assert_eq!(retrieved_metadata.name, "Miss Glestrine Vellum");
    assert_eq!(retrieved_metadata.archetype, "WittySkeptic");
    assert_eq!(retrieved_metadata.state, PersonaState::Active);
}

#[tokio::test]
async fn persona_registry_returns_none_for_nonexistent_persona() {
    let registry = PersonaRegistry::new();
    let nonexistent_id = PersonaId::new(999);

    let result = registry.get(nonexistent_id).unwrap();
    assert!(result.is_none());
}

#[tokio::test]
async fn persona_registry_can_unregister_persona() {
    let registry = PersonaRegistry::new();
    let persona_id = PersonaId::new(1);
    let metadata = PersonaMetadata {
        name: "Mr. Malvo Trevine".to_string(),
        archetype: "BrutalPragmatist".to_string(),
        service_domain: Some("Security".to_string()),
        created_at: Utc::now(),
        last_active: Utc::now(),
        state: PersonaState::Active,
    };

    registry.register(persona_id, metadata).unwrap();
    assert_eq!(registry.count().unwrap(), 1);

    let result = registry.unregister(persona_id);
    assert!(result.is_ok());
    assert_eq!(registry.count().unwrap(), 0);
    assert!(!registry.contains(persona_id).unwrap());
}

#[tokio::test]
async fn persona_registry_handles_unregistering_nonexistent_persona() {
    let registry = PersonaRegistry::new();
    let nonexistent_id = PersonaId::new(999);

    let result = registry.unregister(nonexistent_id);
    assert!(result.is_err());

    match result.unwrap_err() {
        AgentError::PersonaNotFound(id) => assert_eq!(id, nonexistent_id),
        _ => panic!("Expected PersonaNotFound error"),
    }
}

#[tokio::test]
async fn persona_registry_can_update_persona_state() {
    let registry = PersonaRegistry::new();
    let persona_id = PersonaId::new(1);
    let metadata = PersonaMetadata {
        name: "Operant No. 7".to_string(),
        archetype: "PerfectAutomaton".to_string(),
        service_domain: Some("BackgroundServices".to_string()),
        created_at: Utc::now(),
        last_active: Utc::now(),
        state: PersonaState::Inactive,
    };

    registry.register(persona_id, metadata).unwrap();

    // Update state to Active
    let result = registry.update_state(persona_id, PersonaState::Active);
    assert!(result.is_ok());

    let retrieved = registry.get(persona_id).unwrap().unwrap();
    assert_eq!(retrieved.state, PersonaState::Active);
}

#[tokio::test]
async fn persona_registry_can_update_last_active_time() {
    let registry = PersonaRegistry::new();
    let persona_id = PersonaId::new(1);
    let initial_time = Utc::now();
    let metadata = PersonaMetadata {
        name: "Mr. Umbrell Severin".to_string(),
        archetype: "SubtleManipulator".to_string(),
        service_domain: Some("ServiceDiscovery".to_string()),
        created_at: initial_time,
        last_active: initial_time,
        state: PersonaState::Active,
    };

    registry.register(persona_id, metadata).unwrap();

    // Wait a bit to ensure timestamp difference
    tokio::time::sleep(tokio::time::Duration::from_millis(10)).await;

    let result = registry.update_last_active(persona_id);
    assert!(result.is_ok());

    let retrieved = registry.get(persona_id).unwrap().unwrap();
    assert!(retrieved.last_active > initial_time);
}

#[tokio::test]
async fn persona_registry_can_list_all_personas() {
    let registry = PersonaRegistry::new();

    let personas = vec![
        (
            PersonaId::new(1),
            "Madam Calliope Harkthorn",
            "AuthoritativeScholar",
        ),
        (PersonaId::new(2), "Dr. Caudex Thorne", "ClinicalAnalyst"),
        (PersonaId::new(3), "Miss Glestrine Vellum", "WittySkeptic"),
    ];

    for (id, name, archetype) in personas {
        let metadata = PersonaMetadata {
            name: name.to_string(),
            archetype: archetype.to_string(),
            service_domain: None,
            created_at: Utc::now(),
            last_active: Utc::now(),
            state: PersonaState::Inactive,
        };
        registry.register(id, metadata).unwrap();
    }

    let all_personas = registry.list_all().unwrap();
    assert_eq!(all_personas.len(), 3);

    let names: Vec<&str> = all_personas
        .iter()
        .map(|(_, metadata)| metadata.name.as_str())
        .collect();
    assert!(names.contains(&"Madam Calliope Harkthorn"));
    assert!(names.contains(&"Dr. Caudex Thorne"));
    assert!(names.contains(&"Miss Glestrine Vellum"));
}

#[tokio::test]
async fn persona_registry_can_find_by_archetype() {
    let registry = PersonaRegistry::new();

    let metadata1 = PersonaMetadata {
        name: "Scholar 1".to_string(),
        archetype: "AuthoritativeScholar".to_string(),
        service_domain: None,
        created_at: Utc::now(),
        last_active: Utc::now(),
        state: PersonaState::Active,
    };

    let metadata2 = PersonaMetadata {
        name: "Scholar 2".to_string(),
        archetype: "AuthoritativeScholar".to_string(),
        service_domain: None,
        created_at: Utc::now(),
        last_active: Utc::now(),
        state: PersonaState::Inactive,
    };

    let metadata3 = PersonaMetadata {
        name: "Analyst".to_string(),
        archetype: "ClinicalAnalyst".to_string(),
        service_domain: None,
        created_at: Utc::now(),
        last_active: Utc::now(),
        state: PersonaState::Active,
    };

    registry.register(PersonaId::new(1), metadata1).unwrap();
    registry.register(PersonaId::new(2), metadata2).unwrap();
    registry.register(PersonaId::new(3), metadata3).unwrap();

    let scholars = registry.find_by_archetype("AuthoritativeScholar").unwrap();
    assert_eq!(scholars.len(), 2);

    let analysts = registry.find_by_archetype("ClinicalAnalyst").unwrap();
    assert_eq!(analysts.len(), 1);

    let nonexistent = registry.find_by_archetype("NonexistentType").unwrap();
    assert_eq!(nonexistent.len(), 0);
}

#[tokio::test]
async fn persona_registry_can_find_active_personas() {
    let registry = PersonaRegistry::new();

    let active_metadata = PersonaMetadata {
        name: "Active Persona".to_string(),
        archetype: "TestArchetype".to_string(),
        service_domain: None,
        created_at: Utc::now(),
        last_active: Utc::now(),
        state: PersonaState::Active,
    };

    let inactive_metadata = PersonaMetadata {
        name: "Inactive Persona".to_string(),
        archetype: "TestArchetype".to_string(),
        service_domain: None,
        created_at: Utc::now(),
        last_active: Utc::now(),
        state: PersonaState::Inactive,
    };

    registry
        .register(PersonaId::new(1), active_metadata)
        .unwrap();
    registry
        .register(PersonaId::new(2), inactive_metadata)
        .unwrap();

    let active_personas = registry.find_active().unwrap();
    assert_eq!(active_personas.len(), 1);
    assert_eq!(active_personas[0].1.name, "Active Persona");
}
