package com.agrotech.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import com.fasterxml.jackson.annotation.JsonIgnore;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Entidade Conversa - Armazena conversas com IAs
 */
@Entity
@Table(name = "conversas")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Conversa {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "usuario_id", nullable = false)
    @JsonIgnore
    private Usuario usuario;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TipoIA tipoIA;
    
    @Column(nullable = false)
    private String titulo;
    
    @Column(nullable = false)
    private LocalDateTime dataInicio = LocalDateTime.now();
    
    private LocalDateTime dataUltimaMsg;
    
    @OneToMany(mappedBy = "conversa", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("dataEnvio ASC")
    @JsonIgnore
    private List<Mensagem> mensagens = new ArrayList<>();
    
    @Column(nullable = false)
    private Boolean ativa = true;
    
    public enum TipoIA {
        // IAs Educacionais
        PORTUGUES,
        MATEMATICA,
        QUIMICA,
        FISICA,
        BIOLOGIA,
        GEOGRAFIA,
        HISTORIA,
        CIENCIAS,
        
        // IA Agrícola
        AGRO_IA,
        
        // IA do Mercado
        ASSISTENTE_MERCADO
    }
}
