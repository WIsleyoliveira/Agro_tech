package com.agrotech.repository;

import com.agrotech.model.Usuario;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.List;

@Repository
public interface UsuarioRepository extends JpaRepository<Usuario, Long> {
    Optional<Usuario> findByUsername(String username);
    Optional<Usuario> findByEmail(String email);
    List<Usuario> findByTipo(Usuario.TipoUsuario tipo);
    List<Usuario> findByEscola(String escola);
    boolean existsByUsername(String username);
    boolean existsByEmail(String email);
}
