const codeEditor = document.getElementById('codeEditor');
        const submitBtn = document.getElementById('submitBtn');
        const clearBtn = document.getElementById('clearBtn');
        const output = document.getElementById('output');
        const outputContent = document.getElementById('outputContent');

        const SUBMIT_URL = '/api';

        submitBtn.addEventListener('click', async () => {
            const code = codeEditor.value.trim();
            
            if (!code) {
                outputContent.textContent = 'No code to submit!';
                output.classList.add('show');
                return;
            }

            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
            outputContent.textContent = 'Submitting code...';
            output.classList.add('show');

            try {
                const response = await fetch(`${SUBMIT_URL}/scan`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code: code })
                });

                const data = await response.json();

                if (response.ok) {
                    outputContent.innerHTML = `
                        <div class="success-msg">✓ Analysis Complete</div>
                        ${data.errors && data.errors.length > 0 ? `
                            <div class="error-section">
                                <strong>Errors:</strong>
                                ${data.errors.map(err => `<div>${err}</div>`).join('')}
                            </div>
                        ` : ''}
                        
                        <h3>Tokens (${data.tokens.length})</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Type</th>
                                    <th>Lexeme</th>
                                    <th>Line</th>
                                    <th>Column</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.tokens.filter(t => t.type !== 'EOF').map(token => `
                                    <tr>
                                        <td>${token.type}</td>
                                        <td><code>${token.lexeme || ''}</code></td>
                                        <td>${token.line}</td>
                                        <td>${token.col}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                        
                        <h3>Symbol Table</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Identifier</th>
                                    <th>First Line</th>
                                    <th>First Column</th>
                                    <th>Occurrences</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${Object.entries(data.symbol_table || {}).map(([name, info]) => `
                                    <tr>
                                        <td><code>${name}</code></td>
                                        <td>${info.first_line}</td>
                                        <td>${info.first_col}</td>
                                        <td>${info.occurrences}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                } else {
                    outputContent.textContent = `Error: ${data.message || 'Failed to submit code'}`;
                }
            } catch (error) {
                outputContent.textContent = `Network Error: ${error.message}\n\nMake sure to update the SUBMIT_URL in the code to your actual endpoint.`;
            } finally {
                // Reset button state
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Code';
            }

            output.classList.add('show');
        });

        clearBtn.addEventListener('click', () => {
            codeEditor.value = '';
            output.classList.remove('show');
            outputContent.textContent = '';
        });