package com.agrotech.repository;

import com.agrotech.model.Conversa;
import com.agrotech.model.Usuario;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface ConversaRepository extends JpaRepository<Conversa, Long> {
    List<Conversa> findByUsuarioAndAtivaOrderByDataUltimaMsgDesc(Usuario usuario, Boolean ativa);
    List<Conversa> findByUsuarioAndTipoIAOrderByDataUltimaMsgDesc(Usuario usuario, Conversa.TipoIA tipoIA);
    List<Conversa> findByUsuarioOrderByDataUltimaMsgDesc(Usuario usuario);
}
