package com.agrotech.dto;

import lombok.Data;
import jakarta.validation.constraints.NotBlank;

@Data
public class LoginRequest {
    
    @NotBlank(message = "Username ou email é obrigatório")
    private String login; // pode ser username ou email
    
    @NotBlank(message = "Senha é obrigatória")
    private String senha;
}
