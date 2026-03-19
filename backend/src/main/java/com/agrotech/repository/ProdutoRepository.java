package com.agrotech.repository;

import com.agrotech.model.Produto;
import com.agrotech.model.Usuario;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface ProdutoRepository extends JpaRepository<Produto, Long> {
    List<Produto> findByVendedor(Usuario vendedor);
    List<Produto> findByCategoria(Produto.Categoria categoria);
    List<Produto> findByDisponivelTrueOrderByDataCadastroDesc();
    List<Produto> findByOrganicoTrueAndDisponivelTrue();
    List<Produto> findByNomeContainingIgnoreCase(String nome);
}
