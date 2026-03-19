package com.agrotech.controller;

import com.agrotech.dto.*;
import com.agrotech.model.*;
import com.agrotech.service.ConversaService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Controller de Conversas com IA
 */
@RestController
@RequestMapping("/conversas")
@RequiredArgsConstructor
public class ConversaController {
    
    private final ConversaService conversaService;
    
    @PostMapping
    public ResponseEntity<Conversa> criarConversa(
            @Valid @RequestBody ConversaRequest request,
            Authentication authentication) {
        
        String username = authentication.getName();
        Conversa conversa = conversaService.criarConversa(username, request);
        return ResponseEntity.ok(conversa);
    }
    
    @PostMapping("/{conversaId}/mensagens")
    public ResponseEntity<Mensagem> enviarMensagem(
            @PathVariable Long conversaId,
            @Valid @RequestBody MensagemRequest request) {
        
        Mensagem resposta = conversaService.enviarMensagem(conversaId, request.getConteudo());
        return ResponseEntity.ok(resposta);
    }
    
    @GetMapping
    public ResponseEntity<List<Conversa>> listarConversas(Authentication authentication) {
        String username = authentication.getName();
        List<Conversa> conversas = conversaService.listarConversas(username);
        return ResponseEntity.ok(conversas);
    }
    
    @GetMapping("/tipo/{tipoIA}")
    public ResponseEntity<List<Conversa>> listarConversasPorTipo(
            @PathVariable Conversa.TipoIA tipoIA,
            Authentication authentication) {
        
        String username = authentication.getName();
        List<Conversa> conversas = conversaService.listarConversasPorTipo(username, tipoIA);
        return ResponseEntity.ok(conversas);
    }
    
    @GetMapping("/{conversaId}/mensagens")
    public ResponseEntity<List<Mensagem>> obterMensagens(@PathVariable Long conversaId) {
        List<Mensagem> mensagens = conversaService.obterMensagens(conversaId);
        return ResponseEntity.ok(mensagens);
    }
    
    @DeleteMapping("/{conversaId}")
    public ResponseEntity<Void> arquivarConversa(@PathVariable Long conversaId) {
        conversaService.arquivarConversa(conversaId);
        return ResponseEntity.ok().build();
    }
}
