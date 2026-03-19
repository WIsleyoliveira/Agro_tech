package com.agrotech.dto;

import lombok.Data;
import jakarta.validation.constraints.NotBlank;

@Data
public class MensagemRequest {
    
    @NotBlank(message = "Conteúdo da mensagem é obrigatório")
    private String conteudo;
}
