package com.agrotech.service;

import com.agrotech.dto.*;
import com.agrotech.model.Usuario;
import com.agrotech.repository.UsuarioRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;

/**
 * Serviço de autenticação e registro de usuários
 */
@Service
@RequiredArgsConstructor
public class AuthService {
    
    private final UsuarioRepository usuarioRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    
    @Transactional
    public AuthResponse registrar(RegistroRequest request) {
        // Validar se já existe
        if (usuarioRepository.existsByUsername(request.getUsername())) {
            throw new RuntimeException("Username já existe");
        }
        
        if (usuarioRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("Email já existe");
        }
        
        // Criar novo usuário
        Usuario usuario = new Usuario();
        usuario.setUsername(request.getUsername());
        usuario.setEmail(request.getEmail());
        usuario.setSenha(passwordEncoder.encode(request.getSenha()));
        usuario.setNomeCompleto(request.getNomeCompleto());
        usuario.setTipo(request.getTipo());
        
        // Campos específicos por tipo
        if (request.getTipo() == Usuario.TipoUsuario.ESTUDANTE) {
            usuario.setEscola(request.getEscola());
            usuario.setSerie(request.getSerie());
            usuario.setIdade(request.getIdade());
        } else if (request.getTipo() == Usuario.TipoUsuario.AGRICULTOR) {
            usuario.setPropriedade(request.getPropriedade());
            usuario.setLocalizacao(request.getLocalizacao());
            usuario.setAreaHectares(request.getAreaHectares());
        }
        
        usuario = usuarioRepository.save(usuario);
        
        // Gerar token
        String token = jwtService.generateToken(usuario.getUsername());
        
        return new AuthResponse(token, convertToDTO(usuario));
    }
    
    @Transactional
    public AuthResponse login(LoginRequest request) {
        Usuario usuario = usuarioRepository.findByUsername(request.getLogin())
                .orElseGet(() -> usuarioRepository.findByEmail(request.getLogin())
                        .orElseThrow(() -> new BadCredentialsException("Credenciais inválidas")));
        
        if (!passwordEncoder.matches(request.getSenha(), usuario.getSenha())) {
            throw new BadCredentialsException("Credenciais inválidas");
        }
        
        if (!usuario.getAtivo()) {
            throw new RuntimeException("Usuário inativo");
        }
        
        // Atualizar último acesso
        usuario.setUltimoAcesso(LocalDateTime.now());
        usuarioRepository.save(usuario);
        
        // Gerar token
        String token = jwtService.generateToken(usuario.getUsername());
        
        return new AuthResponse(token, convertToDTO(usuario));
    }
    
    private UsuarioDTO convertToDTO(Usuario usuario) {
        UsuarioDTO dto = new UsuarioDTO();
        dto.setId(usuario.getId());
        dto.setUsername(usuario.getUsername());
        dto.setEmail(usuario.getEmail());
        dto.setNomeCompleto(usuario.getNomeCompleto());
        dto.setTipo(usuario.getTipo());
        dto.setEscola(usuario.getEscola());
        dto.setSerie(usuario.getSerie());
        dto.setIdade(usuario.getIdade());
        dto.setPropriedade(usuario.getPropriedade());
        dto.setLocalizacao(usuario.getLocalizacao());
        dto.setAreaHectares(usuario.getAreaHectares());
        dto.setDataCriacao(usuario.getDataCriacao());
        dto.setUltimoAcesso(usuario.getUltimoAcesso());
        return dto;
    }
}
