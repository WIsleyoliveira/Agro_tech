package com.agrotech.controller;

import com.agrotech.model.Produto;
import com.agrotech.model.Usuario;
import com.agrotech.repository.ProdutoRepository;
import com.agrotech.repository.UsuarioRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Controller do Mercado Local
 */
@RestController
@RequestMapping("/mercado")
@RequiredArgsConstructor
public class MercadoController {
    
    private final ProdutoRepository produtoRepository;
    private final UsuarioRepository usuarioRepository;
    
    @GetMapping("/produtos")
    public ResponseEntity<List<Produto>> listarProdutos() {
        List<Produto> produtos = produtoRepository.findByDisponivelTrueOrderByDataCadastroDesc();
        return ResponseEntity.ok(produtos);
    }
    
    @GetMapping("/produtos/categoria/{categoria}")
    public ResponseEntity<List<Produto>> listarPorCategoria(@PathVariable Produto.Categoria categoria) {
        List<Produto> produtos = produtoRepository.findByCategoria(categoria);
        return ResponseEntity.ok(produtos);
    }
    
    @GetMapping("/produtos/organicos")
    public ResponseEntity<List<Produto>> listarOrganicos() {
        List<Produto> produtos = produtoRepository.findByOrganicoTrueAndDisponivelTrue();
        return ResponseEntity.ok(produtos);
    }
    
    @GetMapping("/produtos/buscar")
    public ResponseEntity<List<Produto>> buscarProdutos(@RequestParam String termo) {
        List<Produto> produtos = produtoRepository.findByNomeContainingIgnoreCase(termo);
        return ResponseEntity.ok(produtos);
    }
    
    @PostMapping("/produtos")
    public ResponseEntity<Produto> cadastrarProduto(
            @RequestBody Produto produto,
            Authentication authentication) {
        
        String username = authentication.getName();
        Usuario vendedor = usuarioRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("Usuário não encontrado"));
        
        // Verificar se é agricultor
        if (vendedor.getTipo() != Usuario.TipoUsuario.AGRICULTOR) {
            return ResponseEntity.badRequest().build();
        }
        
        produto.setVendedor(vendedor);
        produto.setDataCadastro(LocalDateTime.now());
        produto = produtoRepository.save(produto);
        
        return ResponseEntity.ok(produto);
    }
    
    @PutMapping("/produtos/{produtoId}")
    public ResponseEntity<Produto> atualizarProduto(
            @PathVariable Long produtoId,
            @RequestBody Produto produtoAtualizado,
            Authentication authentication) {
        
        Produto produto = produtoRepository.findById(produtoId)
                .orElseThrow(() -> new RuntimeException("Produto não encontrado"));
        
        // Verificar se é o dono do produto
        String username = authentication.getName();
        if (!produto.getVendedor().getUsername().equals(username)) {
            return ResponseEntity.status(403).build();
        }
        
        produto.setNome(produtoAtualizado.getNome());
        produto.setDescricao(produtoAtualizado.getDescricao());
        produto.setPreco(produtoAtualizado.getPreco());
        produto.setQuantidadeDisponivel(produtoAtualizado.getQuantidadeDisponivel());
        produto.setDisponivel(produtoAtualizado.getDisponivel());
        produto.setDataAtualizacao(LocalDateTime.now());
        
        produto = produtoRepository.save(produto);
        return ResponseEntity.ok(produto);
    }
    
    @GetMapping("/meus-produtos")
    public ResponseEntity<List<Produto>> meusProdutos(Authentication authentication) {
        String username = authentication.getName();
        Usuario vendedor = usuarioRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("Usuário não encontrado"));
        
        List<Produto> produtos = produtoRepository.findByVendedor(vendedor);
        return ResponseEntity.ok(produtos);
    }
}
