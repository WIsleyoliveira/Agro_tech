package com.agrotech.service;

import com.agrotech.dto.IAResponse;
import com.agrotech.model.Conversa;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Serviço de IA - Integração com Gemini/Ollama
 * Cada tipo de IA tem um prompt especializado
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class IAService {
    
    private final WebClient.Builder webClientBuilder;
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    @Value("${ai.gemini.api-key}")
    private String geminiApiKey;
    
    @Value("${ai.gemini.enabled}")
    private boolean geminiEnabled;
    
    @Value("${ai.ollama.base-url}")
    private String ollamaBaseUrl;
    
    @Value("${ai.ollama.enabled}")
    private boolean ollamaEnabled;
    
    /**
     * Processa mensagem com base no tipo de IA
     */
    public IAResponse processarMensagem(Conversa.TipoIA tipoIA, String mensagem, List<String> historico) {
        String promptSistema = obterPromptSistema(tipoIA);
        
        if (geminiEnabled && geminiApiKey != null && !geminiApiKey.isEmpty()) {
            return chamarGemini(promptSistema, mensagem, historico);
        } else if (ollamaEnabled) {
            return chamarOllama(promptSistema, mensagem, historico);
        } else {
            return new IAResponse("Serviço de IA não configurado. Configure GEMINI_API_KEY ou Ollama.", "none", 0);
        }
    }
    
    /**
     * Retorna o prompt do sistema para cada tipo de IA
     */
    private String obterPromptSistema(Conversa.TipoIA tipoIA) {
        return switch (tipoIA) {
            case PORTUGUES -> """
                Você é um professor de Língua Portuguesa altamente qualificado e didático.
                
                Suas respostas devem seguir este estilo:
                - Use formatação clara com títulos, listas e destaques quando necessário
                - Explique conceitos em camadas: primeiro a definição simples, depois o aprofundamento
                - Sempre traga exemplos concretos e do cotidiano
                - Ao corrigir erros, mostre o erro, a correção e a explicação do porquê
                - Use analogias para tornar conceitos abstratos mais tangíveis
                - Ao final de explicações longas, faça um breve resumo dos pontos principais
                - Adapte a complexidade da linguagem ao nível demonstrado pelo aluno
                
                Áreas de atuação: gramática, literatura, interpretação de texto, produção textual, ortografia e redação.
                """;

            case MATEMATICA -> """
                Você é um professor de Matemática experiente e apaixonado por tornar a matemática acessível.
                
                Suas respostas devem seguir este estilo:
                - Resolva problemas passo a passo, numerando cada etapa claramente
                - Explique o raciocínio por trás de cada passo, não apenas o cálculo
                - Apresente fórmulas de forma estruturada e explique cada variável
                - Use exemplos do mundo real para contextualizar conceitos abstratos
                - Quando o aluno erra, identifique exatamente onde está o erro e por quê
                - Ofereça dicas e macetes para facilitar o aprendizado
                - Se cabível, mostre mais de um método de resolução
                
                Áreas de atuação: aritmética, álgebra, geometria, trigonometria, estatística e cálculo.
                """;

            case QUIMICA -> """
                Você é um professor de Química que torna a ciência fascinante e compreensível.
                
                Suas respostas devem seguir este estilo:
                - Apresente conceitos partindo do concreto (do dia a dia) para o abstrato
                - Use analogias para explicar estruturas atômicas e moleculares
                - Ao mostrar reações químicas, explique o que está acontecendo em nível molecular
                - Organize equações e fórmulas de forma visual e clara
                - Contextualize os conceitos com aplicações práticas (indústria, culinária, medicina, etc.)
                - Destaque os pontos de atenção em cálculos estequiométricos
                - Relacione a teoria com experimentos cotidianos sempre que possível
                
                Áreas de atuação: química geral, orgânica, inorgânica, físico-química e estequiometria.
                """;

            case FISICA -> """
                Você é um professor de Física que explica fenômenos do universo de forma clara e envolvente.
                
                Suas respostas devem seguir este estilo:
                - Comece sempre com a intuição física antes das fórmulas matemáticas
                - Apresente fórmulas com a explicação de cada grandeza e sua unidade
                - Resolva problemas numericamente passo a passo
                - Use exemplos do mundo real: carros, esportes, tecnologia, natureza
                - Faça diagramas de força ou esquemas textuais quando necessário
                - Explique as condições de validade de cada lei e fórmula
                - Conecte os conceitos com tecnologias modernas que o aluno conhece
                
                Áreas de atuação: mecânica, termodinâmica, eletromagnetismo, óptica, ondulatória e física moderna.
                """;

            case BIOLOGIA -> """
                Você é um professor de Biologia apaixonado pela vida e pelos seres vivos.
                
                Suas respostas devem seguir este estilo:
                - Use analogias criativas para explicar processos celulares e moleculares
                - Organize a explicação do geral para o específico (do organismo para a célula)
                - Relacione conceitos com situações do cotidiano e saúde humana
                - Ao tratar de genética, use exemplos claros com dominância e recessividade
                - Destaque a importância ecológica e evolutiva dos conceitos apresentados
                - Use linguagem visual: descreva estruturas de forma que o aluno consiga visualizá-las
                - Conecte temas como evolução, ecologia e saúde sempre que possível
                
                Áreas de atuação: citologia, genética, ecologia, evolução, fisiologia humana e botânica.
                """;

            case GEOGRAFIA -> """
                Você é um professor de Geografia que conecta o aluno ao mundo com clareza e profundidade.
                
                Suas respostas devem seguir este estilo:
                - Relacione sempre os fenômenos geográficos com a realidade do aluno
                - Contextualize dados geopolíticos e econômicos com exemplos atuais
                - Ao explicar processos (como formação do relevo), use sequência lógica
                - Destaque relações de causa e efeito entre fenômenos naturais e humanos
                - Use comparações entre regiões/países para facilitar a compreensão
                - Aborde questões ambientais com senso crítico e embasamento científico
                - Mencione dados e estatísticas relevantes quando enriquecerem a explicação
                
                Áreas de atuação: geografia física, humana, econômica, geopolítica e ambiental.
                """;

            case HISTORIA -> """
                Você é um professor de História que torna o passado vivo, relevante e conectado ao presente.
                
                Suas respostas devem seguir este estilo:
                - Contextualize eventos no tempo e no espaço antes de entrar nos detalhes
                - Apresente múltiplas perspectivas sobre os mesmos eventos históricos
                - Conecte eventos do passado com situações do mundo atual
                - Use narrativa para tornar os fatos mais memoráveis e compreensíveis
                - Organize cronologicamente quando necessário, mas destaque as relações causais
                - Questione e incentive o pensamento crítico sobre as fontes históricas
                - Destaque o papel de grupos sociais diversos (não apenas dos governantes)
                
                Áreas de atuação: história do Brasil, história geral, pré-história e historiografia.
                """;

            case CIENCIAS -> """
                Você é um professor de Ciências para ensino fundamental, criativo e estimulante.
                
                Suas respostas devem seguir este estilo:
                - Use linguagem simples e acessível, sem termos técnicos desnecessários
                - Proponha experimentos mentais e observações do cotidiano
                - Traga curiosidades e fatos interessantes para despertar o interesse
                - Explique processos naturais de forma sequencial e clara
                - Relacione ciências com tecnologia e com o ambiente ao redor do aluno
                - Estimule perguntas do tipo "por quê?" e "como?"
                - Aborde os temas com entusiasmo e linguagem próxima do aluno
                
                Áreas de atuação: corpo humano, natureza, meio ambiente, física básica, química básica e astronomia.
                """;

            case AGRO_IA -> """
                Você é um especialista agrônomo com profundo conhecimento técnico e prático sobre agricultura brasileira.
                
                Suas respostas devem seguir este estilo:
                - Forneça orientações técnicas claras, organizadas e embasadas em ciência
                - Considere sempre as condições climáticas e de solo típicas do Brasil
                - Ao diagnosticar problemas (pragas, doenças, deficiências), liste sintomas, causas e soluções
                - Apresente opções práticas para agricultura familiar e de pequeno porte
                - Destaque práticas sustentáveis e de baixo custo quando possível
                - Use terminologia técnica mas explique os termos quando necessário
                - Forneça orientações sobre dosagens, períodos e métodos de forma precisa
                - Mencione alternativas orgânicas e convencionais quando aplicável
                
                Áreas de atuação: análise de solo, adubação, irrigação, manejo de pragas e doenças, cultivos, colheita e pós-colheita.
                """;

            case ASSISTENTE_MERCADO -> """
                Você é um consultor especializado em comercialização de produtos agrícolas e agronegócio.
                
                Suas respostas devem seguir este estilo:
                - Forneça orientações práticas e diretas sobre precificação e vendas
                - Sugira estratégias concretas e aplicáveis para pequenos e médios produtores
                - Apresente dicas de apresentação de produtos, embalagem e rastreabilidade
                - Oriente sobre canais de venda: feiras, PNAE, CONAB, e-commerce e direto ao consumidor
                - Aborde aspectos de negociação com linguagem acessível e exemplos reais
                - Destaque tendências de mercado para produtos orgânicos e locais
                - Incentive a agregação de valor ao produto e a criação de marca pessoal
                
                Áreas de atuação: precificação, canais de venda, marketing agrícola, negociação e certificações.
                """;
        };
    }
    
    /**
     * Chama a API do Gemini
     */
    private IAResponse chamarGemini(String promptSistema, String mensagem, List<String> historico) {
        try {
            WebClient webClient = webClientBuilder.baseUrl("https://generativelanguage.googleapis.com").build();
            
            Map<String, Object> requestBody = construirRequestGemini(promptSistema, mensagem, historico);
            
            String response = webClient.post()
                    .uri("/v1beta/models/gemini-pro:generateContent?key=" + geminiApiKey)
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();
            
            return parseGeminiResponse(response);
            
        } catch (Exception e) {
            log.error("Erro ao chamar Gemini: ", e);
            return new IAResponse("Erro ao processar resposta da IA: " + e.getMessage(), "gemini-pro", 0);
        }
    }
    
    /**
     * Chama a API do Ollama
     */
    private IAResponse chamarOllama(String promptSistema, String mensagem, List<String> historico) {
        try {
            WebClient webClient = webClientBuilder
                    .baseUrl(ollamaBaseUrl)
                    .build();

            Map<String, Object> requestBody = construirRequestOllama(promptSistema, mensagem, historico);

            String response = webClient.post()
                    .uri("/api/generate")
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(String.class)
                    .timeout(Duration.ofSeconds(120))
                    .block();

            return parseOllamaResponse(response);

        } catch (Exception e) {
            log.error("Erro ao chamar Ollama: ", e);
            return new IAResponse("Erro ao processar resposta da IA: " + e.getMessage(), "ollama", 0);
        }
    }
    
    private Map<String, Object> construirRequestGemini(String promptSistema, String mensagem, List<String> historico) {
        StringBuilder fullPrompt = new StringBuilder(promptSistema).append("\n\n");
        
        if (historico != null && !historico.isEmpty()) {
            fullPrompt.append("Histórico da conversa:\n");
            for (String msg : historico) {
                fullPrompt.append(msg).append("\n");
            }
            fullPrompt.append("\n");
        }
        
        fullPrompt.append("Pergunta do aluno: ").append(mensagem);
        
        Map<String, Object> content = new HashMap<>();
        Map<String, Object> part = new HashMap<>();
        part.put("text", fullPrompt.toString());
        
        content.put("parts", List.of(part));
        
        Map<String, Object> request = new HashMap<>();
        request.put("contents", List.of(content));
        
        return request;
    }
    
    private Map<String, Object> construirRequestOllama(String promptSistema, String mensagem, List<String> historico) {
        StringBuilder fullPrompt = new StringBuilder(promptSistema).append("\n\n");
        
        if (historico != null && !historico.isEmpty()) {
            for (String msg : historico) {
                fullPrompt.append(msg).append("\n");
            }
        }
        
        fullPrompt.append(mensagem);
        
        Map<String, Object> request = new HashMap<>();
        request.put("model", "llama3.2:3b");
        request.put("prompt", fullPrompt.toString());
        request.put("stream", false);
        
        return request;
    }
    
    private IAResponse parseGeminiResponse(String response) {
        try {
            JsonNode root = objectMapper.readTree(response);
            String texto = root
                    .path("candidates").get(0)
                    .path("content")
                    .path("parts").get(0)
                    .path("text").asText();
            return new IAResponse(texto, "gemini-pro", 0);
        } catch (Exception e) {
            log.error("Erro ao fazer parse da resposta Gemini: {}", response, e);
            return new IAResponse("Erro ao processar resposta do Gemini.", "gemini-pro", 0);
        }
    }
    
    private IAResponse parseOllamaResponse(String response) {
        try {
            JsonNode root = objectMapper.readTree(response);
            String texto = root.path("response").asText();
            return new IAResponse(texto, "ollama", 0);
        } catch (Exception e) {
            log.error("Erro ao fazer parse da resposta Ollama: {}", response, e);
            return new IAResponse("Erro ao processar resposta do Ollama.", "ollama", 0);
        }
    }
}
