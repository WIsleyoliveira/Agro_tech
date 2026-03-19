package com.agrotech.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

/**
 * Entidade Progresso - Acompanhamento de estudos dos alunos
 */
@Entity
@Table(name = "progressos")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Progresso {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "usuario_id", nullable = false)
    private Usuario usuario;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Conversa.TipoIA materia;
    
    @Column(nullable = false)
    private String topico;
    
    private Integer questoesRespondidas = 0;
    private Integer questoesCorretas = 0;
    private Integer tempoEstudoMinutos = 0;
    
    @Column(nullable = false)
    private LocalDateTime ultimaAtualizacao = LocalDateTime.now();
    
    // Nível de domínio do tópico (0-100)
    private Integer nivelDominio = 0;
}
