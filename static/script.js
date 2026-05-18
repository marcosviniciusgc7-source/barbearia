const horariosManha = [
    "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00"
];

const horariosTarde = [
    "14:00", "14:30", "15:00", "15:30",
    "16:00", "16:30", "17:00", "17:30",
    "18:00", "18:30"
];

const inputData = document.querySelector('input[name="data"]');
const manha = document.getElementById("manha");
const tarde = document.getElementById("tarde");
const horarioSelecionado = document.getElementById("horarioSelecionado");

flatpickr("#calendario", {
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "d/m/Y",
    locale: "pt",
    minDate: "today",

    disable: [
        function(date) {
            return date.getDay() === 0 || date.getDay() === 1;
        }
    ],

    onChange: function() {
        limparHorarios();
        mostrarHorarios();
    }
});

function proximaEtapa(numero) {
    document.querySelectorAll(".etapa").forEach(etapa => {
        etapa.classList.remove("ativa");
    });

    document.getElementById("etapa" + numero).classList.add("ativa");

    if (numero === 5) {
        mostrarHorarios();
    }
}

function limparHorarios() {
    manha.innerHTML = '<p class="periodo">MANHÃ</p>';
    tarde.innerHTML = '<p class="periodo">TARDE</p>';
    horarioSelecionado.value = "";
    document.getElementById("horarioEscolhido").innerText = "";
}

function criarBotaoHorario(horario, container, ocupados) {
    if (ocupados.includes(horario)) {
        return;
    }

    const botao = document.createElement("button");
    botao.type = "button";
    botao.innerText = horario;
    botao.classList.add("horario-btn");

    botao.addEventListener("click", () => {
        document.querySelectorAll(".horario-btn").forEach(btn => {
            btn.classList.remove("ativo");
        });

        botao.classList.add("ativo");
        horarioSelecionado.value = horario;

        document.getElementById("horarioEscolhido").innerText =
            "Horário escolhido: " + horario;
    });

    container.appendChild(botao);
}

async function mostrarHorarios() {
    limparHorarios();

    if (!inputData.value) {
        return;
    }

    const dataSelecionada = new Date(inputData.value + "T00:00:00");
    const diaSemana = dataSelecionada.getDay();

    if (diaSemana === 0 || diaSemana === 1) {
        manha.innerHTML += "<p class='fechado'>Fechado nesse dia</p>";
        tarde.innerHTML = "";
        return;
    }

    const resposta = await fetch(`/horarios_ocupados?data=${inputData.value}`);
    const ocupados = await resposta.json();

    horariosManha.forEach(horario => {
        criarBotaoHorario(horario, manha, ocupados);
    });

    horariosTarde.forEach(horario => {
        criarBotaoHorario(horario, tarde, ocupados);
    });
}

limparHorarios();