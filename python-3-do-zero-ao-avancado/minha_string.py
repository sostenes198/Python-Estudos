class MinhaString(str):
    def upper(self) -> str:
        print("Sobrescrevi na zueira")
        return super().upper()

custom_string = MinhaString('Soso');

print(custom_string.upper())    