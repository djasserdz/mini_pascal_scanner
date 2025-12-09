const codeEditor = document.getElementById('codeEditor');
const submitBtn = document.getElementById('submitBtn');
const clearBtn = document.getElementById('clearBtn');
const output = document.getElementById('output');
const outputContent = document.getElementById('outputContent');

const SUBMIT_URL = '/api';

function normalizeError(err, idx) {
    if (typeof err === 'string') {
        return { line: 'N/A', col: 'N/A', message: err, idx };
    }
    if (err && typeof err === 'object') {
        return {
            line: err.line !== undefined ? err.line : 'N/A',
            col: err.col !== undefined ? err.col : 'N/A',
            message: err.message || err.msg || JSON.stringify(err),
            idx,
        };
    }
    return { line: 'N/A', col: 'N/A', message: String(err), idx };
}

// Helper function to escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

submitBtn.addEventListener('click', async () => {
    const code = codeEditor.value.trim();
    
    if (!code) {
        outputContent.innerHTML = `
            <div style="
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 12px;
                border-radius: 4px;
                color: #856404;
            ">
                ⚠️ Veuillez entrer du code à analyser
            </div>
        `;
        output.classList.add('show');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Analyse en cours...';
    outputContent.innerHTML = `
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 1.2em; color: #007bff;">⏳ Analyse du code...</div>
        </div>
    `;
    output.classList.add('show');

    try {
        console.log(SUBMIT_URL)
        const response = await fetch(`${SUBMIT_URL}/scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: code })
        });

        const data = await response.json();

        if (response.ok) {
            console.log('Scan Result:', data);
            console.log('Errors:', data.errors);
            console.log('Error type:', typeof data.errors);
            
            // Debug: Check each error
            if (data.errors && data.errors.length > 0) {
                data.errors.forEach((err, i) => {
                    console.log(`Error ${i}:`, err);
                    console.log(`  - line:`, err.line, typeof err.line);
                    console.log(`  - col:`, err.col, typeof err.col);
                    console.log(`  - message:`, err.message, typeof err.message);
                });
            }
            
            // Build the output HTML
            let html = '<div class="success-msg" style="background: #d4edda; padding: 15px; border-radius: 5px; margin-bottom: 20px;">✓ Analyse terminée</div>';
            
            // Display errors if any
            if (data.errors && data.errors.length > 0) {
                const normalizedErrors = data.errors.map((err, i) => normalizeError(err, i));
                html += `
                    <div class="error-section" style="margin-bottom: 30px;">
                        <h3 style="color: #dc3545; margin-bottom: 15px;">
                            ❌ Erreurs détectées (${data.errors.length})
                        </h3>
                        <div style="margin-top: 10px;">
                            ${normalizedErrors.map(({ line, col, message, idx }) => {
                                return `
                                    <div style="
                                        background-color: #fff3f3;
                                        border-left: 4px solid #dc3545;
                                        padding: 12px;
                                        margin-bottom: 10px;
                                        border-radius: 4px;
                                        font-family: monospace;
                                    ">
                                        <div style="font-weight: bold; color: #dc3545; margin-bottom: 5px;">
                                            Erreur #${idx + 1}
                                        </div>
                                        <div style="color: #666; margin-bottom: 3px;">
                                            📍 Ligne ${line}, Colonne ${col}
                                        </div>
                                        <div style="color: #333; margin-top: 5px;">
                                            💬 ${escapeHtml(message)}
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            } else {
                html += `
                    <div style="
                        background-color: #d4edda;
                        border-left: 4px solid #28a745;
                        padding: 12px;
                        border-radius: 4px;
                        color: #155724;
                        margin-bottom: 20px;
                    ">
                        <strong>✅ Aucune erreur détectée</strong>
                        <div style="margin-top: 5px;">Le code source est lexicalement correct.</div>
                    </div>
                `;
            }

            // Display tokens
            const tokensWithoutEOF = data.tokens ? data.tokens.filter(t => t.type !== 'EOF') : [];
            html += `
                <div style="margin-bottom: 30px;">
                    <h3 style="color: #333; margin-bottom: 10px;">
                        🔤 Tokens (${tokensWithoutEOF.length})
                    </h3>
                    ${tokensWithoutEOF.length > 0 ? `
                        <div style="overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                                <thead>
                                    <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                                        <th style="padding: 12px; text-align: left; font-weight: 600;">#</th>
                                        <th style="padding: 12px; text-align: left; font-weight: 600;">Type</th>
                                        <th style="padding: 12px; text-align: left; font-weight: 600;">Lexème</th>
                                        <th style="padding: 12px; text-align: center; font-weight: 600;">Ligne</th>
                                        <th style="padding: 12px; text-align: center; font-weight: 600;">Colonne</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${tokensWithoutEOF.map((token, index) => `
                                        <tr style="border-bottom: 1px solid #dee2e6;">
                                            <td style="padding: 10px; color: #6c757d;">${index + 1}</td>
                                            <td style="padding: 10px;">
                                                <span style="
                                                    background: #e7f3ff;
                                                    color: #0066cc;
                                                    padding: 3px 8px;
                                                    border-radius: 3px;
                                                    font-size: 0.9em;
                                                    font-weight: 500;
                                                ">${escapeHtml(token.type)}</span>
                                            </td>
                                            <td style="padding: 10px;">
                                                <code style="
                                                    background: #f8f9fa;
                                                    padding: 3px 6px;
                                                    border-radius: 3px;
                                                    font-family: 'Courier New', monospace;
                                                ">${escapeHtml(token.lexeme || '')}</code>
                                            </td>
                                            <td style="padding: 10px; text-align: center;">${token.line}</td>
                                            <td style="padding: 10px; text-align: center;">${token.col}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    ` : '<p style="color: #6c757d; font-style: italic;">Aucun token trouvé.</p>'}
                </div>
            `;

            // Display symbol table
            const symbolEntries = data.symbol_table ? Object.entries(data.symbol_table) : [];
            html += `
                <div style="margin-bottom: 30px;">
                    <h3 style="color: #333; margin-bottom: 10px;">
                        📋 Table des Symboles (${symbolEntries.length})
                    </h3>
                    ${symbolEntries.length > 0 ? `
                        <div style="overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                                <thead>
                                    <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                                        <th style="padding: 12px; text-align: left; font-weight: 600;">#</th>
                                        <th style="padding: 12px; text-align: left; font-weight: 600;">Identificateur</th>
                                        <th style="padding: 12px; text-align: center; font-weight: 600;">Première Ligne</th>
                                        <th style="padding: 12px; text-align: center; font-weight: 600;">Première Colonne</th>
                                        <th style="padding: 12px; text-align: center; font-weight: 600;">Occurrences</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${symbolEntries.map(([name, info], index) => `
                                        <tr style="border-bottom: 1px solid #dee2e6;">
                                            <td style="padding: 10px; color: #6c757d;">${index + 1}</td>
                                            <td style="padding: 10px;">
                                                <code style="
                                                    background: #fff3e0;
                                                    color: #e65100;
                                                    padding: 3px 8px;
                                                    border-radius: 3px;
                                                    font-family: 'Courier New', monospace;
                                                    font-weight: 500;
                                                ">${escapeHtml(name)}</code>
                                            </td>
                                            <td style="padding: 10px; text-align: center;">${info.first_line}</td>
                                            <td style="padding: 10px; text-align: center;">${info.first_col}</td>
                                            <td style="padding: 10px; text-align: center;">
                                                <span style="
                                                    background: #e8f5e9;
                                                    color: #2e7d32;
                                                    padding: 3px 8px;
                                                    border-radius: 3px;
                                                    font-weight: 500;
                                                ">${info.occurrences}</span>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    ` : '<p style="color: #6c757d; font-style: italic;">Aucun identificateur trouvé.</p>'}
                </div>
            `;

            // Display success status
            if (data.success !== undefined) {
                html += `
                    <div style="
                        background-color: ${data.success ? '#d4edda' : '#f8d7da'};
                        border-left: 4px solid ${data.success ? '#28a745' : '#dc3545'};
                        padding: 12px;
                        border-radius: 4px;
                        color: ${data.success ? '#155724' : '#721c24'};
                        margin-top: 20px;
                    ">
                        <strong>${data.success ? '✅ Succès' : '❌ Échec'}</strong>
                        <div style="margin-top: 5px;">
                            ${data.success ? 
                                'L\'analyse lexicale est terminée sans erreur.' : 
                                'L\'analyse lexicale a rencontré des erreurs.'
                            }
                        </div>
                    </div>
                `;
            }

            outputContent.innerHTML = html;
        } else {
            outputContent.innerHTML = `
                <div style="
                    background-color: #f8d7da;
                    border-left: 4px solid #dc3545;
                    padding: 12px;
                    border-radius: 4px;
                    color: #721c24;
                ">
                    <strong>❌ Erreur Serveur</strong>
                    <div style="margin-top: 5px;">${escapeHtml(data.message || 'Échec de l\'analyse du code')}</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error:', error);
        outputContent.innerHTML = `
            <div style="
                background-color: #f8d7da;
                border-left: 4px solid #dc3545;
                padding: 12px;
                border-radius: 4px;
                color: #721c24;
            ">
                <strong>❌ Erreur Réseau</strong>
                <div style="margin-top: 5px;">${escapeHtml(error.message)}</div>
                <div style="margin-top: 10px; font-size: 0.9em; color: #6c757d;">
                    Assurez-vous que le serveur backend est en cours d'exécution et que SUBMIT_URL est correctement configuré.
                </div>
            </div>
        `;
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        submitBtn.textContent = 'Analyser le Code';
    }

    output.classList.add('show');
});

clearBtn.addEventListener('click', () => {
    codeEditor.value = '';
    output.classList.remove('show');
    outputContent.innerHTML = '';
});