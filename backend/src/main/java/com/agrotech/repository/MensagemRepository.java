package com.agrotech.repository;

import com.agrotech.model.Mensagem;
import com.agrotech.model.Conversa;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface MensagemRepository extends JpaRepository<Mensagem, Long> {
    List<Mensagem> findByConversaOrderByDataEnvioAsc(Conversa conversa);
}
