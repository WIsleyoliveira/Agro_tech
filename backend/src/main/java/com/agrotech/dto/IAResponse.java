package com.agrotech.dto;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class IAResponse {
    private String resposta;
    private String modelo;
    private Integer tokensUsados;
}
