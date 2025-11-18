document.addEventListener('DOMContentLoaded', function() {
    // Elementos do DOM
    const estadoOrigemSelect = document.getElementById('estado-origem');
    const cidadeOrigemSelect = document.getElementById('cidade-origem');
    const estadoDestinoSelect = document.getElementById('estado-destino');
    const cidadeDestinoSelect = document.getElementById('cidade-destino');
    const consultaForm = document.getElementById('consultaForm');
    const resultContainer = document.getElementById('resultContainer');
    const resultContent = document.getElementById('resultContent');
    
    // Armazenar dados das cidades para acesso posterior
    let cidadesOrigem = {};
    let cidadesDestino = {};
    
    // Sistema de Captcha com Texto Alfanumérico Aleatório
    let captchaData = {
        currentCode: '',
        isVerified: false
    };

    // Funções do Captcha com Texto Alfanumérico Aleatório
    function gerarNovaPerguntaCaptcha() {
        // Gerar código alfanumérico aleatório de 6 caracteres
        const caracteres = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        let codigo = '';
        
        for (let i = 0; i < 6; i++) {
            codigo += caracteres.charAt(Math.floor(Math.random() * caracteres.length));
        }
        
        captchaData.currentCode = codigo;
        captchaData.isVerified = false;
        
        // Atualizar a interface
        const captchaQuestion = document.getElementById('captchaQuestion');
        const captchaAnswer = document.getElementById('captchaAnswer');
        const captchaStatus = document.getElementById('captchaStatus');
        
        if (captchaQuestion) {
            captchaQuestion.textContent = `Digite o código: ${captchaData.currentCode}`;
        }
        
        if (captchaAnswer) {
            captchaAnswer.value = '';
            captchaAnswer.classList.remove('success', 'error');
        }
        
        if (captchaStatus) {
            captchaStatus.textContent = '';
            captchaStatus.className = 'captcha-status';
        }
    }
    
    function verificarCaptcha() {
        const captchaAnswer = document.getElementById('captchaAnswer');
        const captchaStatus = document.getElementById('captchaStatus');
        
        if (!captchaAnswer || !captchaStatus) return false;
        
        const userAnswer = captchaAnswer.value.trim().toUpperCase();
        const correctAnswer = captchaData.currentCode.toUpperCase();
        
        // Verificar se a resposta está correta (comparação exata, case insensitive)
        const isCorrect = userAnswer === correctAnswer;
        
        if (isCorrect) {
            captchaData.isVerified = true;
            captchaAnswer.classList.remove('error');
            captchaAnswer.classList.add('success');
            captchaStatus.textContent = '✅ Verificação concluída!';
            captchaStatus.className = 'captcha-status success';
            return true;
        } else {
            captchaData.isVerified = false;
            captchaAnswer.classList.remove('success');
            captchaAnswer.classList.add('error');
            captchaStatus.textContent = '❌ Código incorreto. Tente novamente.';
            captchaStatus.className = 'captcha-status error';
            return false;
        }
    }
    
    function inicializarCaptcha() {
        // Gerar primeira pergunta
        gerarNovaPerguntaCaptcha();
        
        // Event listener para o botão de refresh
        const btnRefreshCaptcha = document.getElementById('btnRefreshCaptcha');
        if (btnRefreshCaptcha) {
            btnRefreshCaptcha.addEventListener('click', function() {
                gerarNovaPerguntaCaptcha();
                
                // Feedback visual
                const originalText = btnRefreshCaptcha.textContent;
                btnRefreshCaptcha.textContent = '✨';
                btnRefreshCaptcha.style.background = '#10B981';
                
                setTimeout(() => {
                    btnRefreshCaptcha.textContent = originalText;
                    btnRefreshCaptcha.style.background = '';
                }, 1000);
            });
        }
        
        // Event listener para validação em tempo real
        const captchaAnswer = document.getElementById('captchaAnswer');
        if (captchaAnswer) {
            captchaAnswer.addEventListener('input', function() {
                // Limpar estados anteriores
                this.classList.remove('success', 'error');
                const captchaStatus = document.getElementById('captchaStatus');
                if (captchaStatus) {
                    captchaStatus.textContent = '';
                    captchaStatus.className = 'captcha-status';
                }
                captchaData.isVerified = false;
            });
            
            captchaAnswer.addEventListener('blur', function() {
                if (this.value.trim()) {
                    verificarCaptcha();
                }
            });
        }
    }

    // Função para carregar cidades baseado no estado selecionado
    function carregarCidades(estadoSelect, cidadeSelect) {
        if (!estadoSelect || !cidadeSelect) {
            console.error('Elementos de estado ou cidade não encontrados');
            return;
        }
        
        const estadoId = estadoSelect.value;
        
        if (!estadoId) {
            cidadeSelect.innerHTML = '<option value="">Primeiro selecione o estado</option>';
            cidadeSelect.disabled = true;
            return;
        }

        // Mostrar loading
        cidadeSelect.innerHTML = '<option value="">Carregando cidades...</option>';
        cidadeSelect.disabled = true;

        // Fazer requisição AJAX
        fetch(`/api/cidades/?estado_id=${estadoId}`)
            .then(response => response.json())
            .then(data => {
                cidadeSelect.innerHTML = '<option value="">Selecione a cidade</option>';
                
                // Remover duplicatas baseado no nome (case insensitive)
                const cidadesUnicas = [];
                const nomesVistos = new Set();
                
                data.forEach(cidade => {
                    const nomeUpper = cidade.nome.toUpperCase();
                    if (!nomesVistos.has(nomeUpper)) {
                        nomesVistos.add(nomeUpper);
                        cidadesUnicas.push(cidade);
                    }
                });
                
                // Ordenar cidades alfabeticamente
                cidadesUnicas.sort((a, b) => a.nome.localeCompare(b.nome));
                
                cidadesUnicas.forEach(cidade => {
                    const option = document.createElement('option');
                    option.value = cidade.id;
                    option.textContent = cidade.nome.toUpperCase();
                    option.className = 'notranslate'; // Adicionar classe para não traduzir
                    cidadeSelect.appendChild(option);
                    
                    // Armazenar dados da cidade para uso posterior
                    if (cidadeSelect.id === 'cidade-origem') {
                        cidadesOrigem[cidade.id] = cidade;
                    } else if (cidadeSelect.id === 'cidade-destino') {
                        cidadesDestino[cidade.id] = cidade;
                    }
                });
                
                cidadeSelect.disabled = false;
            })
            .catch(error => {
                console.error('Erro ao carregar cidades:', error);
                cidadeSelect.innerHTML = '<option value="">Erro ao carregar cidades</option>';
                cidadeSelect.disabled = true;
            });
    }

    // Event listeners para os selects de estado
    if (estadoOrigemSelect && cidadeOrigemSelect) {
        estadoOrigemSelect.addEventListener('change', function() {
            carregarCidades(estadoOrigemSelect, cidadeOrigemSelect);
        });
    }

    if (estadoDestinoSelect && cidadeDestinoSelect) {
        estadoDestinoSelect.addEventListener('change', function() {
            carregarCidades(estadoDestinoSelect, cidadeDestinoSelect);
        });
    }

    // Event listener para o botão de limpar
    const btnLimpar = document.getElementById('btnLimpar');
    if (btnLimpar) {
        btnLimpar.addEventListener('click', function() {
            limparFormulario();
        });
    }

    // Função para limpar o formulário
    function limparFormulario() {
        // Limpar seleções dos estados
        estadoOrigemSelect.value = '';
        estadoDestinoSelect.value = '';
        
        // Limpar e desabilitar selects de cidades
        cidadeOrigemSelect.innerHTML = '<option value="">Primeiro selecione o estado</option>';
        cidadeOrigemSelect.disabled = true;
        cidadeDestinoSelect.innerHTML = '<option value="">Primeiro selecione o estado</option>';
        cidadeDestinoSelect.disabled = true;
        
        // Limpar dados armazenados
        cidadesOrigem = {};
        cidadesDestino = {};
        
        // Limpar captcha
        gerarNovaPerguntaCaptcha();
        
        // Ocultar resultado se estiver visível
        const resultContainer = document.getElementById('resultContainer');
        if (resultContainer) {
            resultContainer.style.display = 'none';
        }
        
        // Adicionar efeito visual de limpeza
        const formGroups = document.querySelectorAll('.form-group');
        formGroups.forEach(group => {
            group.classList.remove('filled');
            const select = group.querySelector('.form-select');
            if (select) {
                select.style.borderColor = 'var(--cor-cinza-claro)';
            }
        });
        
        // Feedback visual no botão
        const btnLimpar = document.getElementById('btnLimpar');
        if (btnLimpar) {
            const originalText = btnLimpar.innerHTML;
            btnLimpar.innerHTML = '<span class="btn-text">✅ Limpo!</span><span class="btn-icon">✨</span>';
            btnLimpar.style.background = '#10B981';
            
            setTimeout(() => {
                btnLimpar.innerHTML = originalText;
                btnLimpar.style.background = '';
            }, 1500);
        }
        
        // Focar no primeiro campo
        estadoOrigemSelect.focus();
    }

    // Função para calcular nível de risco baseado nas posições
    function calcularNivelRisco(posicaoOrigem, posicaoDestino) {
        // Se alguma posição não estiver disponível, usar simulação
        if (posicaoOrigem === 'N/A' || posicaoDestino === 'N/A' || 
            posicaoOrigem === null || posicaoDestino === null ||
            posicaoOrigem === undefined || posicaoDestino === undefined) {
            const niveisRisco = ['Baixo', 'Médio', 'Alto'];
            return {
                nivel: niveisRisco[Math.floor(Math.random() * niveisRisco.length)],
                tipo: 'simulado'
            };
        }

        // Garantir que as posições são números
        const posOrigemNum = Number(posicaoOrigem);
        const posDestinoNum = Number(posicaoDestino);
        
        // Validar se a conversão foi bem-sucedida
        if (isNaN(posOrigemNum) || isNaN(posDestinoNum)) {
            const niveisRisco = ['Baixo', 'Médio', 'Alto'];
            return {
                nivel: niveisRisco[Math.floor(Math.random() * niveisRisco.length)],
                tipo: 'simulado'
            };
        }

        const diferenca = posDestinoNum - posOrigemNum;
        
        if (diferenca > 0) {
            return {
                nivel: 'Reduzido',
                tipo: 'calculado',
                diferenca: diferenca
            };
        } else if (diferenca == 0) {
            return {
                nivel: 'Inalterado',
                tipo: 'calculado',
                diferenca: diferenca
            };
        } else {
            return {
                nivel: 'Aumentado',
                tipo: 'calculado',
                diferenca: Math.abs(diferenca)
            };
        }
    }

    // Função para obter cor baseada no nível de risco
    function obterCorRisco(nivel) {
        const cores = {
            'Baixo': '#10B981', // Verde
            'Médio': '#F59E0B', // Amarelo
            'Alto': '#EF4444',  // Vermelho
            'Reduzido': '#10B981', // Verde
            'Aumentado': '#EF4444',  // Vermelho
            'Inalterado': '#2D3748' // Cinza escuro
        };
        return cores[nivel] || '#6B7280';
    }

    // Função para obter ícone baseado no nível de risco
    function obterIconeRisco(nivel) {
        const icones = {
            'Baixo': '✅',
            'Médio': '⚠️',
            'Alto': '🚨',
            'Reduzido': '📉',
            'Aumentado': '📈',
            'Inalterado': '🔄'
        };
        return icones[nivel] || '❓';
    }

    // Event listener para o formulário (apenas se existir)
    if (consultaForm && consultaForm.id === 'consultaForm') {
        consultaForm.addEventListener('submit', function(e) {
            e.preventDefault();
        
        // Verificar se os elementos existem
        if (!estadoOrigemSelect || !cidadeOrigemSelect || !estadoDestinoSelect || !cidadeDestinoSelect) {
            console.error('Elementos do formulário não encontrados');
            alert('Erro: Elementos do formulário não encontrados. Por favor, recarregue a página.');
            return;
        }
        
        const estadoOrigem = estadoOrigemSelect.options[estadoOrigemSelect.selectedIndex].text;
        const cidadeOrigemId = cidadeOrigemSelect.value;
        const cidadeOrigem = cidadeOrigemSelect.options[cidadeOrigemSelect.selectedIndex].text;
        const estadoDestino = estadoDestinoSelect.options[estadoDestinoSelect.selectedIndex].text;
        const cidadeDestinoId = cidadeDestinoSelect.value;
        const cidadeDestino = cidadeDestinoSelect.options[cidadeDestinoSelect.selectedIndex].text;
        
        // Obter posições das cidades
        const cidadeOrigemData = cidadesOrigem[cidadeOrigemId];
        const cidadeDestinoData = cidadesDestino[cidadeDestinoId];
        const posicaoOrigem = (cidadeOrigemData && cidadeOrigemData.posicao !== null && cidadeOrigemData.posicao !== undefined) 
            ? cidadeOrigemData.posicao 
            : 'N/A';
        const posicaoDestino = (cidadeDestinoData && cidadeDestinoData.posicao !== null && cidadeDestinoData.posicao !== undefined) 
            ? cidadeDestinoData.posicao 
            : 'N/A';

        // Validar se todos os campos foram preenchidos
        if (!cidadeOrigem || !cidadeDestino || cidadeOrigem === 'Selecione a cidade' || cidadeDestino === 'Selecione a cidade') {
            alert('Por favor, selecione todas as cidades de origem e destino.');
            return;
        }

        // Validar captcha
        if (!captchaData.isVerified) {
            const captchaAnswer = document.getElementById('captchaAnswer');
            if (!captchaAnswer || !captchaAnswer.value.trim()) {
                alert('Por favor, responda à pergunta de verificação antes de consultar.');
                captchaAnswer.focus();
                return;
            }
            
            // Tentar verificar o captcha
            if (!verificarCaptcha()) {
                alert('Resposta incorreta. Por favor, tente novamente ou gere uma nova pergunta.');
                captchaAnswer.focus();
                return;
            }
        }

        // Mostrar loading no botão
        const submitBtn = consultaForm.querySelector('.btn-primary');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="btn-text">Consultando...</span><span class="btn-icon">⏳</span>';
        submitBtn.disabled = true;

        // Simular delay da consulta
        setTimeout(() => {
            const resultado = calcularNivelRisco(posicaoOrigem, posicaoDestino);
            
            // Construir HTML do resultado
            const corRisco = obterCorRisco(resultado.nivel);
            const iconeRisco = obterIconeRisco(resultado.nivel);
            
            // Buscar médias das avaliações
            if (typeof buscarMediaAvaliacoes === 'function' && typeof exibirResultado === 'function') {
                buscarMediaAvaliacoes(estadoOrigemSelect.value, cidadeOrigem, estadoDestinoSelect.value, cidadeDestino, function(mediaOrigem, mediaDestino) {
                    exibirResultado(resultado, corRisco, iconeRisco, cidadeOrigem, estadoOrigem, posicaoOrigem, cidadeDestino, estadoDestino, posicaoDestino, mediaOrigem, mediaDestino, originalText, submitBtn);
                });
            } else {
                console.error('Funções buscarMediaAvaliacoes ou exibirResultado não encontradas');
                // Exibir resultado sem avaliações se as funções não estiverem disponíveis
                const resultContent = document.getElementById('resultContent');
                const resultContainer = document.getElementById('resultContainer');
                if (resultContent && resultContainer) {
                    resultContent.innerHTML = `
                        <div class="result-header">
                            <h3 style="color: ${corRisco}; margin-bottom: 1rem;">
                                ${iconeRisco} Nível de Risco: ${resultado.nivel}
                            </h3>
                            ${resultado.tipo === 'calculado' ? `
                                <p style="font-size: 0.9rem; color: var(--cor-cinza); margin-bottom: 1rem;">
                                    Diferença de posições: ${resultado.diferenca} posições
                                </p>
                            ` : ''}
                            <p style="margin-bottom: 1.5rem; font-size: 1.1rem;">
                                <strong>Trajeto:</strong> ${cidadeOrigem.toUpperCase()} (${estadoOrigem}) → ${cidadeDestino.toUpperCase()} (${estadoDestino})
                            </p>
                        </div>
                    `;
                    resultContainer.style.display = 'block';
                    resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
                // Restaurar botão
                if (submitBtn && originalText) {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }
            }
        }, 1500);
        });
    }
    
    // Função para buscar média de avaliações
    function buscarMediaAvaliacoes(estadoOrigemId, cidadeOrigem, estadoDestinoId, cidadeDestino, callback) {
        let mediaOrigem = null;
        let mediaDestino = null;
        let chamadasCompletas = 0;
        
        // Buscar média da cidade origem
        fetch(`/api/media-avaliacoes/?estado_id=${estadoOrigemId}&cidade=${encodeURIComponent(cidadeOrigem)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.tem_avaliacoes) {
                    mediaOrigem = data.media;
                }
                chamadasCompletas++;
                if (chamadasCompletas === 2) {
                    callback(mediaOrigem, mediaDestino);
                }
            })
            .catch(error => {
                console.error('Erro ao buscar média de avaliações origem:', error);
                chamadasCompletas++;
                if (chamadasCompletas === 2) {
                    callback(mediaOrigem, mediaDestino);
                }
            });
        
        // Buscar média da cidade destino
        fetch(`/api/media-avaliacoes/?estado_id=${estadoDestinoId}&cidade=${encodeURIComponent(cidadeDestino)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.tem_avaliacoes) {
                    mediaDestino = data.media;
                }
                chamadasCompletas++;
                if (chamadasCompletas === 2) {
                    callback(mediaOrigem, mediaDestino);
                }
            })
            .catch(error => {
                console.error('Erro ao buscar média de avaliações destino:', error);
                chamadasCompletas++;
                if (chamadasCompletas === 2) {
                    callback(mediaOrigem, mediaDestino);
                }
            });
    }
    
    // Função para exibir resultado com avaliações
    function exibirResultado(resultado, corRisco, iconeRisco, cidadeOrigem, estadoOrigem, posicaoOrigem, cidadeDestino, estadoDestino, posicaoDestino, mediaOrigem, mediaDestino, originalText, submitBtn) {
        const resultContent = document.getElementById('resultContent');
        const resultContainer = document.getElementById('resultContainer');
        
        // Função auxiliar para formatar avaliação
        function formatarAvaliacao(media) {
            if (media !== null && media !== undefined) {
                return `<div style="margin-top: 0.5rem; font-size: 0.9rem; color: var(--cor-azul-escuro);">
                    <strong>Avaliação Usuários:</strong> ${media}/10
                </div>`;
            } else {
                return `<div style="margin-top: 0.5rem; font-size: 0.9rem; color: var(--cor-cinza); font-style: italic;">
                    Cidade sem avaliações de usuários.
                </div>`;
            }
        }
        
        resultContent.innerHTML = `
                <div class="result-header">
                    <h3 style="color: ${corRisco}; margin-bottom: 1rem;">
                        ${iconeRisco} Nível de Risco: ${resultado.nivel}
                    </h3>
                    ${resultado.tipo === 'calculado' ? `
                        <p style="font-size: 0.9rem; color: var(--cor-cinza); margin-bottom: 1rem;">
                            Diferença de posições: ${resultado.diferenca} posições
                        </p>
                    ` : ''}
                    <p style="margin-bottom: 1.5rem; font-size: 1.1rem;">
                        <strong>Trajeto:</strong> ${cidadeOrigem.toUpperCase()} (${estadoOrigem}) → ${cidadeDestino.toUpperCase()} (${estadoDestino})
                    </p>
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                        <h4 style="color: var(--cor-azul-escuro); margin-bottom: 0.75rem; font-size: 1rem;">City Score Ranking de Criminalidade:</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; text-align: center;">
                            <div>
                                <strong style="color: var(--cor-laranja);">Origem:</strong><br>
                                ${cidadeOrigem.toUpperCase()}<br>
                                <small style="color: var(--cor-cinza);">${estadoOrigem}</small><br>
                                <span style="font-size: 1.2rem; font-weight: bold; color: var(--cor-azul-escuro);">#${posicaoOrigem}</span>
                                ${formatarAvaliacao(mediaOrigem)}
                            </div>
                            <div>
                                <strong style="color: var(--cor-laranja);">Destino:</strong><br>
                                ${cidadeDestino.toUpperCase()}<br>
                                <small style="color: var(--cor-cinza);">${estadoDestino}</small><br>
                                <span style="font-size: 1.2rem; font-weight: bold; color: var(--cor-azul-escuro);">#${posicaoDestino}</span>
                                ${formatarAvaliacao(mediaDestino)}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Seção de Avaliação de Segurança -->
                <div class="avaliacao-section" style="margin-top: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 12px; border: 1px solid var(--cor-cinza-claro);">
                    <h4 style="color: var(--cor-azul-escuro); margin-bottom: 1rem; font-size: 1.2rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">⭐</span>
                        Avalie o Nível de Segurança da sua Cidade de Origem
                    </h4>
                    <p style="color: var(--cor-cinza); margin-bottom: 1.5rem; font-size: 0.95rem;">
                        Sua opinião é importante! Ajude outros usuários compartilhando sua experiência sobre a segurança de <strong>${cidadeOrigem.toUpperCase()}</strong>.
                    </p>
                    
                    <form id="avaliacaoForm" style="display: grid; gap: 1rem;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                            <div>
                                <label style="display: block; margin-bottom: 0.5rem; font-weight: 600; color: var(--cor-azul-escuro);">Seu Email:</label>
                                <input type="email" id="emailAvaliacao" required 
                                       style="width: 100%; padding: 0.75rem; border: 1px solid var(--cor-cinza-claro); border-radius: 6px; font-size: 0.95rem;"
                                       placeholder="seu@email.com">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 0.5rem; font-weight: 600; color: var(--cor-azul-escuro);">Nota (1-10):</label>
                                <select id="notaAvaliacao" required 
                                        style="width: 100%; padding: 0.75rem; border: 1px solid var(--cor-cinza-claro); border-radius: 6px; font-size: 0.95rem;">
                                    <option value="">Selecione uma nota</option>
                                    <option value="1">1 - Muito Inseguro</option>
                                    <option value="2">2 - Muito Inseguro</option>
                                    <option value="3">3 - Inseguro</option>
                                    <option value="4">4 - Inseguro</option>
                                    <option value="5">5 - Neutro</option>
                                    <option value="6">6 - Seguro</option>
                                    <option value="7">7 - Seguro</option>
                                    <option value="8">8 - Muito Seguro</option>
                                    <option value="9">9 - Muito Seguro</option>
                                    <option value="10">10 - Extremamente Seguro</option>
                                </select>
                            </div>
                        </div>
                        
                        <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                            <button type="submit" id="btnAvaliar" 
                                    style="background: var(--cor-laranja); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; gap: 0.5rem;">
                                <span>⭐ Avaliar</span>
                            </button>
                            <button type="button" id="btnMapaSeguranca" 
                                    style="background: var(--cor-azul-escuro); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; gap: 0.5rem;">
                                <span>🗺️ Veja o mapa da Segurança</span>
                            </button>
                            <div id="avaliacaoStatus" style="font-size: 0.9rem; font-weight: 500;"></div>
                        </div>
                    </form>
                </div>
                
                <div class="result-footer" style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid var(--cor-cinza-claro);">
                    <p style="font-size: 0.9rem; color: var(--cor-cinza);">
                        <em>⚠️ Fonte de dados abertos usados no cálculo do ranking: Ministério da Justiça e Segurança Pública, IBGE. A metodologia aplicada no cálculo do Score de Ranking não tem nenhum vínculo com estas instituições, bem como os resultados informados. Ranking atualizado mensalmente com base em dados do ano corrente e anterior, contemplando mais de 5 mil cidades do país.</em>
                    </p>
                </div>
            `;
        
        // Mostrar resultado com animação
        resultContainer.style.display = 'block';
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Configurar evento do formulário de avaliação
        const estadoOrigemSelectElement = document.getElementById('estado-origem');
        if (estadoOrigemSelectElement) {
            configurarAvaliacaoForm(estadoOrigemSelectElement.value, cidadeOrigem);
        }
        
        // Configurar botão do mapa de segurança
        const btnMapaSeguranca = document.getElementById('btnMapaSeguranca');
        if (btnMapaSeguranca) {
            btnMapaSeguranca.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Salvar texto original
                const originalText = btnMapaSeguranca.innerHTML;
                
                // Alterar texto e desabilitar botão
                btnMapaSeguranca.innerHTML = '<span>⏳ Carregando mapa...</span>';
                btnMapaSeguranca.disabled = true;
                btnMapaSeguranca.style.opacity = '0.7';
                btnMapaSeguranca.style.cursor = 'wait';
                
                // Redirecionar para a página do mapa
                window.location.href = '/mapa-seguranca/';
            });
        }
        
        // Restaurar botão
        if (submitBtn && originalText) {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    // Função para configurar o formulário de avaliação
    function configurarAvaliacaoForm(estadoId, cidadeNome) {
        const avaliacaoForm = document.getElementById('avaliacaoForm');
        const btnAvaliar = document.getElementById('btnAvaliar');
        const avaliacaoStatus = document.getElementById('avaliacaoStatus');
        
        if (!avaliacaoForm) return;
        
        avaliacaoForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('emailAvaliacao').value.trim();
            const nota = parseInt(document.getElementById('notaAvaliacao').value);
            
            // Validações
            if (!email) {
                mostrarStatusAvaliacao('Por favor, digite seu email.', 'error');
                return;
            }
            
            if (!nota || nota < 1 || nota > 10) {
                mostrarStatusAvaliacao('Por favor, selecione uma nota válida.', 'error');
                return;
            }
            
            // Mostrar loading
            btnAvaliar.disabled = true;
            btnAvaliar.innerHTML = '<span>⏳ Enviando...</span>';
            mostrarStatusAvaliacao('Enviando avaliação...', 'loading');
            
            // Enviar avaliação
            fetch('/api/avaliar-seguranca/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    email: email,
                    estado_id: estadoId,
                    cidade: cidadeNome,
                    nota: nota
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mensagem personalizada baseada se foi criada ou atualizada
                    let statusMessage = '';
                    if (data.created) {
                        statusMessage = `✅ ${data.message} Nota: ${data.nota}/10`;
                        btnAvaliar.innerHTML = '<span>✅ Avaliado!</span>';
                    } else {
                        statusMessage = `🔄 ${data.message} Nota: ${data.nota}/10 (Atualizada em: ${data.data_avaliacao} - Horário de Brasília)`;
                        btnAvaliar.innerHTML = '<span>🔄 Atualizado!</span>';
                    }
                    
                    mostrarStatusAvaliacao(statusMessage, 'success');
                    btnAvaliar.style.background = '#10B981';
                    
                    // Limpar formulário após sucesso
                    setTimeout(() => {
                        document.getElementById('emailAvaliacao').value = '';
                        document.getElementById('notaAvaliacao').value = '';
                        btnAvaliar.innerHTML = '<span>⭐ Avaliar</span>';
                        btnAvaliar.style.background = 'var(--cor-laranja)';
                        btnAvaliar.disabled = false;
                        avaliacaoStatus.textContent = '';
                    }, 4000); // Aumentei o tempo para 4 segundos para dar tempo de ler a mensagem
                } else {
                    mostrarStatusAvaliacao(`❌ ${data.error}`, 'error');
                    btnAvaliar.innerHTML = '<span>⭐ Avaliar</span>';
                    btnAvaliar.disabled = false;
                }
            })
            .catch(error => {
                console.error('Erro ao enviar avaliação:', error);
                mostrarStatusAvaliacao('❌ Erro ao enviar avaliação. Tente novamente.', 'error');
                btnAvaliar.innerHTML = '<span>⭐ Avaliar</span>';
                btnAvaliar.disabled = false;
            });
        });
    }
    
    // Função para mostrar status da avaliação
    function mostrarStatusAvaliacao(mensagem, tipo) {
        const avaliacaoStatus = document.getElementById('avaliacaoStatus');
        if (!avaliacaoStatus) return;
        
        avaliacaoStatus.textContent = mensagem;
        
        // Remover classes anteriores
        avaliacaoStatus.classList.remove('success', 'error', 'loading');
        
        // Adicionar classe baseada no tipo
        if (tipo === 'success') {
            avaliacaoStatus.style.color = '#10B981';
        } else if (tipo === 'error') {
            avaliacaoStatus.style.color = '#EF4444';
        } else if (tipo === 'loading') {
            avaliacaoStatus.style.color = '#F59E0B';
        }
    }

    // Função para animar elementos quando entram na tela
    function observarElementos() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Observar elementos do formulário
        const formElements = document.querySelectorAll('.form-container, .hero');
        formElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
            observer.observe(el);
        });
    }

    // Inicializar observador de elementos
    observarElementos();

    // Função para adicionar efeitos visuais aos selects
    function adicionarEfeitosVisuais() {
        const selects = document.querySelectorAll('.form-select');
        
        selects.forEach(select => {
            select.addEventListener('focus', function() {
                this.parentElement.style.transform = 'scale(1.02)';
                this.parentElement.style.transition = 'transform 0.2s ease-out';
            });
            
            select.addEventListener('blur', function() {
                this.parentElement.style.transform = 'scale(1)';
            });
        });
    }

    // Inicializar efeitos visuais
    adicionarEfeitosVisuais();

    // Função para adicionar feedback visual ao formulário
    function adicionarFeedbackVisual() {
        const formGroups = document.querySelectorAll('.form-group');
        
        formGroups.forEach(group => {
            const select = group.querySelector('.form-select');
            
            select.addEventListener('change', function() {
                if (this.value) {
                    group.classList.add('filled');
                    this.style.borderColor = 'var(--cor-laranja)';
                } else {
                    group.classList.remove('filled');
                    this.style.borderColor = 'var(--cor-cinza-claro)';
                }
            });
        });
    }

    // Inicializar feedback visual
    adicionarFeedbackVisual();
    
    // Inicializar captcha
    inicializarCaptcha();

    console.log('Sistema de consulta de risco carregado com sucesso!');
    console.log('Estado Origem Select:', estadoOrigemSelect);
    console.log('Cidade Origem Select:', cidadeOrigemSelect);
    console.log('Estado Destino Select:', estadoDestinoSelect);
    console.log('Cidade Destino Select:', cidadeDestinoSelect);
    console.log('Função carregarCidades:', typeof carregarCidades);
    console.log('Função buscarMediaAvaliacoes:', typeof buscarMediaAvaliacoes);
    console.log('Função exibirResultado:', typeof exibirResultado);
    
    // Configurar Google Translate para não traduzir elementos específicos
    function configureGoogleTranslate() {
        // Aguardar o Google Translate carregar
        setTimeout(() => {
            // Adicionar classe notranslate aos elementos que não devem ser traduzidos
            const elementsToExclude = [
                '.cupom-badge',
                '.notranslate',
                'option[class*="notranslate"]'
            ];
            
            elementsToExclude.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    element.classList.add('notranslate');
                });
            });
            
            console.log('Google Translate configurado para excluir elementos específicos');
        }, 2000);
    }
    
    // Executar configuração quando o DOM estiver pronto
    configureGoogleTranslate();

    // Copiar cupom Mercado Livre
    const copyButtons = document.querySelectorAll('.copy-coupon');
    copyButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const code = btn.getAttribute('data-code') || 'CITYSAFETY10';
            navigator.clipboard.writeText(code).then(() => {
                const original = btn.innerHTML;
                btn.innerHTML = '<span class="btn-text">Copiado!</span>';
                setTimeout(() => {
                    btn.innerHTML = original;
                }, 1500);
            }).catch(() => {
                // fallback sem revelar o cupom na UI
                const textarea = document.createElement('textarea');
                textarea.value = code;
                textarea.setAttribute('readonly', '');
                textarea.style.position = 'absolute';
                textarea.style.left = '-9999px';
                document.body.appendChild(textarea);
                textarea.select();
                try {
                    document.execCommand('copy');
                    const original = btn.innerHTML;
                    btn.innerHTML = '<span class="btn-text">Copiado!</span>';
                    setTimeout(() => { btn.innerHTML = original; }, 1500);
                } catch (e) {
                    alert('Copie manualmente o cupom.');
                }
                document.body.removeChild(textarea);
            });
        });
    });
});

// Banner de Política de Privacidade e Cookies
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando banner de privacidade...');
    
    // Aguardar um pouco para garantir que o DOM está completamente carregado
    setTimeout(function() {
        const banner = document.getElementById('privacyBanner');
        const acceptAllBtn = document.getElementById('acceptAllPrivacy');
        const overlay = document.getElementById('privacyOverlay');
        
        console.log('Elementos encontrados:', {
            banner: !!banner,
            acceptAllBtn: !!acceptAllBtn,
            overlay: !!overlay
        });
        
        // Verificar se os elementos existem
        if (!banner) {
            console.error('Banner não encontrado!');
            return;
        }
        
        if (!acceptAllBtn) {
            console.error('Botão aceitar não encontrado!');
        }
        
        if (!overlay) {
            console.error('Overlay não encontrado!');
        }
        
        // Verificar se é a primeira visita na sessão atual
        const privacyShownInSession = sessionStorage.getItem('privacyShownInSession');
        console.log('Modal já mostrado nesta sessão:', privacyShownInSession);
        
        // Mostrar banner apenas na primeira visita da sessão
        if (!privacyShownInSession) {
            setTimeout(() => {
                console.log('Exibindo banner na primeira visita...');
                banner.style.display = 'block';
                overlay.style.display = 'block';
                
                // Marcar que o modal foi mostrado nesta sessão
                sessionStorage.setItem('privacyShownInSession', 'true');
                
                // Adicionar padding-bottom ao body para compensar o banner
                document.body.style.paddingBottom = banner.offsetHeight + 'px';
                
                // Bloquear scroll da página
                document.body.style.overflow = 'hidden';
            }, 1000); // Mostrar após 1 segundo
        } else {
            console.log('Modal já foi mostrado nesta sessão, não exibindo novamente.');
        }
        
        // Função para fechar o banner
        function closeBanner() {
            console.log('Fechando banner...');
            banner.style.display = 'none';
            overlay.style.display = 'none';
            document.body.style.paddingBottom = '0';
            document.body.style.overflow = 'auto';
        }
        
        // Event listeners
        if (acceptAllBtn) {
            acceptAllBtn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Botão aceitar clicado');
                // Salva no localStorage para referência (persistente entre sessões)
                localStorage.setItem('privacyAccepted', 'all');
                localStorage.setItem('privacyAcceptedDate', new Date().toISOString());
                closeBanner();
                showNotification('Termos e condições aceitos!', 'success');
            };
        }
        
        // Bloquear cliques no overlay
        if (overlay) {
            overlay.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Tentativa de clique no overlay bloqueada');
                return false;
            };
        }
        
        // Bloquear navegação por teclado quando overlay está ativo
        document.addEventListener('keydown', function(e) {
            if (overlay && overlay.style.display === 'block') {
                // Bloquear teclas de navegação
                if (e.key === 'Tab' || e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Navegação por teclado bloqueada');
                    return false;
                }
            }
        });
        
        // Bloquear formulários quando overlay está ativo
        document.addEventListener('submit', function(e) {
            if (overlay && overlay.style.display === 'block') {
                e.preventDefault();
                e.stopPropagation();
                console.log('Envio de formulário bloqueado');
                showNotification('Você deve aceitar os cookies antes de continuar.', 'warning');
                return false;
            }
        });
        
        // Bloquear links quando overlay está ativo
        document.addEventListener('click', function(e) {
            if (overlay && overlay.style.display === 'block') {
                const target = e.target;
                if (target.tagName === 'A' || target.closest('a')) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Navegação por link bloqueada');
                    showNotification('Você deve aceitar os cookies antes de continuar.', 'warning');
                    return false;
                }
            }
        });
        
        
    }, 100); // Aguardar 100ms para garantir que o DOM está pronto
    
    // Função para mostrar notificações
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Estilos da notificação
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10001;
            animation: slideInRight 0.3s ease-out;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        `;
        
        // Cores baseadas no tipo
        if (type === 'success') {
            notification.style.backgroundColor = '#28a745';
        } else if (type === 'error') {
            notification.style.backgroundColor = '#dc3545';
        } else {
            notification.style.backgroundColor = '#17a2b8';
        }
        
        document.body.appendChild(notification);
        
        // Remover após 4 segundos
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
    
    // Adicionar animações CSS para notificações
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});

