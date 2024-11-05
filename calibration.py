import curses
from gpiozero import PWMOutputDevice
from time import sleep

# Configuração do PWM no pino GPIO 18
servo_pwm = PWMOutputDevice(18, frequency=50)  # Frequência de 50 Hz para servos

def set_servo_pulse(pulse_width):
    # Converte a largura do pulso para o ciclo de trabalho apropriado
    duty_cycle = pulse_width / 0.02  # 20 ms de período para 50 Hz
    servo_pwm.value = duty_cycle  # Define o ciclo de trabalho diretamente

# Configurações de pulso mínimo e máximo para o MG996R
min_pulse = 0.0005
max_pulse = 0.0025
pulse_width = 0.0015  # Começa em 0 graus aproximadamente

def get_pulse(angle):
    # Calcula a largura do pulso PWM para um ângulo específico
    pulse_width = min_pulse + ((angle + 90) / 180) * (max_pulse - min_pulse)
    return pulse_width

def main(stdscr):
    global pulse_width  # Declare a variável pulse_width como global
    # Inicializa o curses e limpa a tela
    curses.curs_set(0)  # Oculta o cursor
    stdscr.clear()
    stdscr.addstr(0, 0, "Use as setas para cima e para baixo para ajustar o pulso.")
    stdscr.addstr(1, 0, "Pressione 'Enter' para confirmar o ângulo.")
    stdscr.addstr(2, 0, "Pressione 'q' para sair.")
    stdscr.addstr(4, 0, "Ângulo Atual: 0 graus")
    stdscr.addstr(5, 0, f"Pulso PWM: {pulse_width:.6f} segundos")

    angle_neg_45 = None
    angle_pos_45 = None

    while True:
        # Aguarda uma tecla ser pressionada
        key = stdscr.getch()

        # Ajusta o pulso com base na tecla pressionada
        if key == curses.KEY_UP:
            pulse_width += 0.000005
            pulse_width = min(pulse_width, max_pulse)
            angle = -90 + (180 * (pulse_width - min_pulse) / (max_pulse - min_pulse))
            stdscr.addstr(4, 0, f"Ângulo Atual: {angle:.2f} graus    ")
            stdscr.addstr(5, 0, f"Pulso PWM: {pulse_width:.6f} segundos")
            set_servo_pulse(pulse_width)  # Atualiza o servo
            stdscr.refresh()
            #sleep(0.1)

        elif key == curses.KEY_DOWN:
            pulse_width -= 0.000005
            pulse_width = max(pulse_width, min_pulse)
            angle = -90 + (180 * (pulse_width - min_pulse) / (max_pulse - min_pulse))
            stdscr.addstr(4, 0, f"Ângulo Atual: {angle:.2f} graus    ")
            stdscr.addstr(5, 0, f"Pulso PWM: {pulse_width:.6f} segundos")
            set_servo_pulse(pulse_width)  # Atualiza o servo
            stdscr.refresh()
            #sleep(0.1)

        # Confirma o ângulo ao pressionar 'Enter'
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if angle_neg_45 is None:
                angle_neg_45 = angle
                stdscr.addstr(6, 0, f"Ângulo -45 confirmado: {angle_neg_45:.2f} graus  ")
            elif angle_pos_45 is None:
                angle_pos_45 = angle
                stdscr.addstr(7, 0, f"Ângulo +45 confirmado: {angle_pos_45:.2f} graus  ")

            # Verifica se ambos os ângulos foram confirmados
            if angle_neg_45 is not None and angle_pos_45 is not None:
                pulse_neg_45 = get_pulse(angle_neg_45)
                pulse_pos_45 = get_pulse(angle_pos_45)
                pulse_center = (pulse_neg_45 + pulse_pos_45) / 2
                stdscr.addstr(8, 0, f"Pulso Médio para 0 graus: {pulse_center:.6f} segundos ")
                set_servo_pulse(pulse_center)
                stdscr.refresh()

        # Sai do loop ao pressionar 'q'
        elif key == ord('q'):
            break

    # Desativa o PWM ao sair
    servo_pwm.off()

# Inicia o curses
curses.wrapper(main)
