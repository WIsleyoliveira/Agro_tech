package com.agrotech.service;

import com.agrotech.dto.*;
import com.agrotech.model.*;
import com.agrotech.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Serviço de gerenciamento de conversas
 */
@Service
@RequiredArgsConstructor
public class ConversaService {
    
    private final ConversaRepository conversaRepository;
    private final MensagemRepository mensagemRepository;
    private final UsuarioRepository usuarioRepository;
    private final IAService iaService;
    
    @Transactional
    public Conversa criarConversa(String username, ConversaRequest request) {
        Usuario usuario = usuarioRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("Usuário não encontrado"));
        
        Conversa conversa = new Conversa();
        conversa.setUsuario(usuario);
        conversa.setTipoIA(request.getTipoIA());
        conversa.setTitulo(request.getTitulo());
        conversa.setDataUltimaMsg(LocalDateTime.now());
        
        conversa = conversaRepository.save(conversa);
        
        // Se tem mensagem inicial, processar
        if (request.getMensagemInicial() != null && !request.getMensagemInicial().isEmpty()) {
            enviarMensagem(conversa.getId(), request.getMensagemInicial());
        }
        
        return conversa;
    }
    
    @Transactional
    public Mensagem enviarMensagem(Long conversaId, String conteudo) {
        Conversa conversa = conversaRepository.findById(conversaId)
                .orElseThrow(() -> new RuntimeException("Conversa não encontrada"));
        
        // Salvar mensagem do usuário
        Mensagem mensagemUsuario = new Mensagem();
        mensagemUsuario.setConversa(conversa);
        mensagemUsuario.setRemetente(Mensagem.TipoRemetente.USUARIO);
        mensagemUsuario.setConteudo(conteudo);
        mensagemRepository.save(mensagemUsuario);
        
        // Obter histórico para contexto
        List<String> historico = obterHistoricoConversa(conversa);
        
        // Processar com IA
        IAResponse respostaIA = iaService.processarMensagem(
                conversa.getTipoIA(),
                conteudo,
                historico
        );
        
        // Salvar resposta da IA
        Mensagem mensagemIA = new Mensagem();
        mensagemIA.setConversa(conversa);
        mensagemIA.setRemetente(Mensagem.TipoRemetente.IA);
        mensagemIA.setConteudo(respostaIA.getResposta());
        mensagemIA.setModelo(respostaIA.getModelo());
        mensagemIA.setTokensUsados(respostaIA.getTokensUsados());
        mensagemRepository.save(mensagemIA);
        
        // Atualizar data da última mensagem
        conversa.setDataUltimaMsg(LocalDateTime.now());
        conversaRepository.save(conversa);
        
        return mensagemIA;
    }
    
    public List<Conversa> listarConversas(String username) {
        Usuario usuario = usuarioRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("Usuário não encontrado"));
        
        return conversaRepository.findByUsuarioOrderByDataUltimaMsgDesc(usuario);
    }
    
    public List<Conversa> listarConversasPorTipo(String username, Conversa.TipoIA tipoIA) {
        Usuario usuario = usuarioRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("Usuário não encontrado"));
        
        return conversaRepository.findByUsuarioAndTipoIAOrderByDataUltimaMsgDesc(usuario, tipoIA);
    }
    
    public List<Mensagem> obterMensagens(Long conversaId) {
        Conversa conversa = conversaRepository.findById(conversaId)
                .orElseThrow(() -> new RuntimeException("Conversa não encontrada"));
        
        return mensagemRepository.findByConversaOrderByDataEnvioAsc(conversa);
    }
    
    @Transactional
    public void arquivarConversa(Long conversaId) {
        Conversa conversa = conversaRepository.findById(conversaId)
                .orElseThrow(() -> new RuntimeException("Conversa não encontrada"));
        
        conversa.setAtiva(false);
        conversaRepository.save(conversa);
    }
    
    private List<String> obterHistoricoConversa(Conversa conversa) {
        List<Mensagem> mensagens = mensagemRepository.findByConversaOrderByDataEnvioAsc(conversa);
        
        // Limitar histórico às últimas 10 mensagens para não sobrecarregar
        return mensagens.stream()
                .skip(Math.max(0, mensagens.size() - 10))
                .map(m -> m.getRemetente() == Mensagem.TipoRemetente.USUARIO 
                        ? "Aluno: " + m.getConteudo() 
                        : "Professor: " + m.getConteudo())
                .collect(Collectors.toList());
    }
}
