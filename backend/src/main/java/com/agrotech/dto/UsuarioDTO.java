package com.agrotech.dto;

import com.agrotech.model.Usuario;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class UsuarioDTO {
    private Long id;
    private String username;
    private String email;
    private String nomeCompleto;
    private Usuario.TipoUsuario tipo;
    private String escola;
    private String serie;
    private Integer idade;
    private String propriedade;
    private String localizacao;
    private Double areaHectares;
    private LocalDateTime dataCriacao;
    private LocalDateTime ultimoAcesso;
}
