package com.agrotech.repository;

import com.agrotech.model.Progresso;
import com.agrotech.model.Usuario;
import com.agrotech.model.Conversa;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface ProgressoRepository extends JpaRepository<Progresso, Long> {
    List<Progresso> findByUsuario(Usuario usuario);
    List<Progresso> findByUsuarioAndMateria(Usuario usuario, Conversa.TipoIA materia);
    Optional<Progresso> findByUsuarioAndMateriaAndTopico(Usuario usuario, Conversa.TipoIA materia, String topico);
}
