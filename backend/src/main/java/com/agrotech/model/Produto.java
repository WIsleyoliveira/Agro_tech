package com.agrotech.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

/**
 * Entidade Produto - Produtos do mercado local
 */
@Entity
@Table(name = "produtos")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Produto {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "vendedor_id", nullable = false)
    private Usuario vendedor;
    
    @Column(nullable = false)
    private String nome;
    
    @Column(columnDefinition = "TEXT")
    private String descricao;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Categoria categoria;
    
    @Column(nullable = false)
    private Double preco;
    
    @Column(nullable = false)
    private String unidade; // kg, unidade, dúzia, etc
    
    private Double quantidadeDisponivel;
    
    private String imagemUrl;
    
    @Column(nullable = false)
    private Boolean organico = false;
    
    @Column(nullable = false)
    private Boolean disponivel = true;
    
    @Column(nullable = false)
    private LocalDateTime dataCadastro = LocalDateTime.now();
    
    private LocalDateTime dataAtualizacao;
    
    public enum Categoria {
        FRUTAS,
        VERDURAS,
        LEGUMES,
        GRAOS,
        LATICINIOS,
        OVOS,
        MEL,
        OUTROS
    }
}
