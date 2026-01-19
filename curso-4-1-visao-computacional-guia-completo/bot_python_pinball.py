import mss
import numpy as np
import cv2
import pyautogui
import time
import keyboard

# --- CONFIGURAÇÃO ---
# Você precisará ajustar essa região para onde o jogo aparece na sua tela.
# Use um programa de print screen para pegar as coordenadas (top, left, width, height)
GAME_REGION = {"top": 200, "left": 400, "width": 600, "height": 800}

# Cores da bola (no formato BGR do OpenCV - Blue, Green, Red)
# Isso depende do jogo. Se a bola for prata/cinza, é mais difícil.
# Se for um jogo online colorido, pegue a cor aproximada.
LOWER_COLOR = np.array([180, 180, 180])  # Cinza claro
UPPER_COLOR = np.array([255, 255, 255])  # Branco

# Posição Y onde os flippers estão (Zona de Gatilho)
FLIPPER_TRIGGER_Y = 650


def process_frame(sct):
    # 1. Capturar tela (O OLHO)
    screenshot = np.array(sct.grab(GAME_REGION))

    # Remover canal Alpha se existir e garantir que o array seja contíguo na memória
    # O erro "Layout of the output array img is incompatible" acontece sem isso
    frame = np.ascontiguousarray(screenshot[:, :, :3])

    # 2. Processamento (VISÃO COMPUTACIONAL)
    # Criar uma máscara para achar a bola (baseado na cor)
    mask = cv2.inRange(frame, LOWER_COLOR, UPPER_COLOR)

    # Encontrar contornos (formas brancas na máscara preta)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    ball_pos = None

    for contour in contours:
        area = cv2.contourArea(contour)
        # Filtrar ruídos pequenos (pixel morto) ou grandes (títulos)
        if 20 < area < 1000:
            # Pegar o centro do círculo
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                ball_pos = (cX, cY)

                # Desenhar caixa verde em volta da bola para debug
                cv2.circle(frame, (cX, cY), 10, (0, 255, 0), 2)
                break  # Assumimos que achamos a bola

    return frame, ball_pos


def main():
    print("--- PINBALL BOT INICIADO ---")
    print("Posicione a janela do jogo na região configurada.")
    print("Pressione 'q' para sair.")

    # Inicializa capturador de tela ultrarrápido
    with mss.mss() as sct:
        while True:
            # Sair se 'q' for pressionado
            if keyboard.is_pressed('q'):
                print("Encerrando...")
                break

            # Processar visão
            frame, ball_pos = process_frame(sct)

            # 3. Decisão (O CÉREBRO)
            if ball_pos:
                bx, by = ball_pos

                # Desenhar linha de gatilho no debug
                cv2.line(frame, (0, FLIPPER_TRIGGER_Y), (GAME_REGION['width'], FLIPPER_TRIGGER_Y), (0, 0, 255), 2)

                # Lógica: Se a bola passou da linha vermelha (perto dos flippers)
                if by > FLIPPER_TRIGGER_Y:

                    # Decidir qual flipper usar baseado no lado da tela
                    center_x = GAME_REGION['width'] // 2

                    if bx < center_x:
                        print(f"Bola na Esquerda ({bx},{by}) -> FLIPPER ESQ")
                        pyautogui.press('left')  # Seta Esquerda
                    else:
                        print(f"Bola na Direita ({bx},{by}) -> FLIPPER DIR")
                        pyautogui.press('right')  # Seta Direita

                    # Pequeno delay para não "spamar" o teclado e travar o PC
                    # Em IA profissional, removemos isso, mas para testes é segurança.
                    time.sleep(0.1)

                    # Mostrar o que a IA está vendo (janela de debug)
            cv2.imshow('Visao da IA', frame)

            # Necessário para janela do OpenCV atualizar
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()