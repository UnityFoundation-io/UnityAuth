package io.unityfoundation.auth.entities;

import io.micronaut.data.annotation.GeneratedValue;
import io.micronaut.data.annotation.Id;
import io.micronaut.data.annotation.MappedEntity;

@MappedEntity
public class Role {
    @Id
    @GeneratedValue
    private Long id;

    private String name;
    private String description;
}
