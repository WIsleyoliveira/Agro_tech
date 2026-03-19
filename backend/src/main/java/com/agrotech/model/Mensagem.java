package com.agrotech.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import com.fasterxml.jackson.annotation.JsonIgnore;
import java.time.LocalDateTime;

/**
 * Entidade Mensagem - Mensagens individuais em conversas
 */
@Entity
@Table(name = "mensagens")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Mensagem {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "conversa_id", nullable = false)
    @JsonIgnore
    private Conversa conversa;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TipoRemetente remetente;
    
    @Column(nullable = false, columnDefinition = "TEXT")
    private String conteudo;
    
    @Column(nullable = false)
    private LocalDateTime dataEnvio = LocalDateTime.now();
    
    // Metadados adicionais
    private String modelo; // Qual modelo de IA foi usado
    private Integer tokensUsados;
    
    public enum TipoRemetente {
        USUARIO,
        IA
    }
}
