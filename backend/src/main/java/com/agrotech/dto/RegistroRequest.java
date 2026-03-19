package com.agrotech.dto;

import com.agrotech.model.Usuario;
import lombok.Data;
import jakarta.validation.constraints.*;

@Data
public class RegistroRequest {
    
    @NotBlank(message = "Username é obrigatório")
    @Size(min = 3, max = 50)
    private String username;
    
    @NotBlank(message = "Email é obrigatório")
    @Email(message = "Email inválido")
    private String email;
    
    @NotBlank(message = "Senha é obrigatória")
    @Size(min = 6, message = "Senha deve ter no mínimo 6 caracteres")
    private String senha;
    
    @NotBlank(message = "Nome completo é obrigatório")
    private String nomeCompleto;
    
    @NotNull(message = "Tipo de usuário é obrigatório")
    private Usuario.TipoUsuario tipo;
    
    // Campos para estudantes
    private String escola;
    private String serie;
    private Integer idade;
    
    // Campos para agricultores
    private String propriedade;
    private String localizacao;
    private Double areaHectares;
}
