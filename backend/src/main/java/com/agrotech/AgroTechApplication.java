package com.agrotech;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * AgroTech Platform - Sistema de Ensino e Agronegócio
 * 
 * Plataforma completa que integra:
 * - IA Educacional para estudantes (todas as matérias)
 * - Agro.IA para agricultores (análise de solo, cultivos)
 * - Mercado Local (comércio de produtos agrícolas)
 */
@SpringBootApplication
public class AgroTechApplication {
    public static void main(String[] args) {
        SpringApplication.run(AgroTechApplication.class, args);
    }
}
