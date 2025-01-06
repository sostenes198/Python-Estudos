import json

import tensorflow as tf

class RnKeras:
    __HISTORY_TRAIN_JSON_FILE_NAME: str = 'history_train_rn.json'
    __KERAS_TRAINED_MODEL_FILE_NAME: str= 'rn_bart_home.keras'

    def __init__(self):
        ...

    def train(self, X_train, Y_train) -> None:
        # input_shape será igual a quantidade de pixels da imagem mutliplando a altura vs a lagura
        # O calculo simples do unit será a formula: (16384) + 2) / 2
        # ONDE 16384  Quantidade de neurônios da camada de entrada
        # ONDE 2 é a Quantidade de classes (Homer e Bart)
        network1 = tf.keras.models.Sequential()
        network1.add(tf.keras.layers.Dense(input_shape=(16384,), units=8193, activation='relu'))
        network1.add(tf.keras.layers.Dense(units=8193, activation='relu'))
        network1.add(
            tf.keras.layers.Dense(units=1, activation='sigmoid'))  # retorna um valor entre 0 e 1, uma probabilidade

        # print(network1.summary())
        network1.compile(optimizer='Adam', loss='binary_crossentropy', metrics=['accuracy'])

        # batch_size=128, validation_data=(X_test, Y_test)
        history = network1.fit(X_train, Y_train, epochs=50, )

        network1.save(self.__KERAS_TRAINED_MODEL_FILE_NAME)

        # Salvar o histórico em um arquivo JSON
        with open(self.__HISTORY_TRAIN_JSON_FILE_NAME, "w") as f:
            json.dump(history.history, f)

    def load_nr(self,):
        model = tf.keras.models.load_model(self.__KERAS_TRAINED_MODEL_FILE_NAME)
        loaded_history = None

        with open(self.__HISTORY_TRAIN_JSON_FILE_NAME, "r") as f:
            loaded_history = json.load(f)

        return model, loaded_history,

