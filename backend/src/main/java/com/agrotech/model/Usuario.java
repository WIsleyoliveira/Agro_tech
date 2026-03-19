package com.agrotech.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import com.fasterxml.jackson.annotation.JsonIgnore;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

/**
 * Entidade Usuario - Representa todos os tipos de usuário da plataforma
 */
@Entity
@Table(name = "usuarios")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Usuario {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String username;
    
    @Column(nullable = false, unique = true)
    private String email;
    
    @Column(nullable = false)
    @JsonIgnore
    private String senha;
    
    @Column(nullable = false)
    private String nomeCompleto;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TipoUsuario tipo;
    
    // Campos específicos para estudantes
    private String escola;
    private String serie;
    private Integer idade;
    
    // Campos específicos para agricultores
    private String propriedade;
    private String localizacao;
    private Double areaHectares;
    
    @Column(nullable = false)
    private Boolean ativo = true;
    
    @Column(nullable = false)
    private LocalDateTime dataCriacao = LocalDateTime.now();
    
    private LocalDateTime ultimoAcesso;
    
    @OneToMany(mappedBy = "usuario", cascade = CascadeType.ALL)
    @JsonIgnore
    private Set<Conversa> conversas = new HashSet<>();
    
    @OneToMany(mappedBy = "usuario", cascade = CascadeType.ALL)
    @JsonIgnore
    private Set<Progresso> progressos = new HashSet<>();
    
    public enum TipoUsuario {
        ESTUDANTE,
        AGRICULTOR,
        ADMIN
    }
}
