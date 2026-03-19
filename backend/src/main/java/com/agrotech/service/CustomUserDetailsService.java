package com.agrotech.service;

import com.agrotech.model.Usuario;
import com.agrotech.repository.UsuarioRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import java.util.Collections;

/**
 * Serviço de autenticação customizado
 */
@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {
    
    private final UsuarioRepository usuarioRepository;
    
    @Override
    public UserDetails loadUserByUsername(String login) throws UsernameNotFoundException {
        Usuario usuario = usuarioRepository.findByUsername(login)
                .orElseGet(() -> usuarioRepository.findByEmail(login)
                        .orElseThrow(() -> new UsernameNotFoundException("Usuário não encontrado: " + login)));
        
        return User.builder()
                .username(usuario.getUsername())
                .password(usuario.getSenha())
                .authorities(Collections.emptyList())
                .accountExpired(false)
                .accountLocked(!usuario.getAtivo())
                .credentialsExpired(false)
                .disabled(!usuario.getAtivo())
                .build();
    }
}
