const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

// Faz o efeito de deslizar do vídeo
signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});


// Redirecionamento para as páginas de sucesso

// Quando clicar no botão de entrar no LOGIN
document.getElementById('form-signin').addEventListener('submit', (e) => {
    e.preventDefault(); 
    // Manda para a página de carregamento que está na outra pasta
    window.location.href = "../cadastro e login sucesso/login.html";
});

// Lógica de Cadastro com Validação de Senha
document.getElementById('form-signup').addEventListener('submit', (e) => {
    e.preventDefault();
    
    const senha = document.getElementById('senha').value;
    const confirma = document.getElementById('confirmar_senha').value;

    if (senha !== confirma) {
        alert("As senhas não coincidem! Por favor, tente novamente.");
        return; 
    }

    // Se estiver tudo ok, vai para a página de "Salvando..."
    window.location.href = "../cadastro e login sucesso/cadastro.html";
});