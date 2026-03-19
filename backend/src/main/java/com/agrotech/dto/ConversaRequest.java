package com.agrotech.dto;

import com.agrotech.model.Conversa;
import lombok.Data;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

@Data
public class ConversaRequest {
    
    @NotNull(message = "Tipo de IA é obrigatório")
    private Conversa.TipoIA tipoIA;
    
    @NotBlank(message = "Título é obrigatório")
    private String titulo;
    
    private String mensagemInicial;
}
