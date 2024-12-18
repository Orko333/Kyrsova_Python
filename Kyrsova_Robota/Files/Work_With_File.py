from Files import Configs as con
import re

def file_write():
    """
    Записує конфігураційні налаштування у файл.
    """
    with open('Files/config_file', 'w+') as file:
        file.write(f"current_language = {con.current_language}\n")
        file.write(f"volume = {con.volume}\n")
        file.write(f"resolution_index = {con.resolution_index}\n")
        file.write(f"fullscreen = {con.fullscreen}\n")

def file_read():
    """
    Зчитує конфігураційні налаштування з файлу та встановлює їх у конфігурації.
    """
    with open('Files/config_file', 'r') as file:
        lines = file.readlines()
        for line in lines:
            match = re.match(r"(\w+) = ([\w.]+)", line)
            if match:
                key, value = match.groups()
                if key == "volume":
                    setattr(con, key, float(value))
                else:
                    try:
                        setattr(con, key, int(value))
                    except ValueError:
                        setattr(con, key, value)

def file_read_U():
    """
    Зчитує українські переклади з файлу та повертає їх у вигляді словника.
    """
    with open('Files/translations_ua', 'r', encoding='utf-8') as file:
        ua = {}
        for line in file:
            line = line.strip()
            if ": " in line:
                key, value = line.split(": ", 1)
                key = key.strip('"')
                value = value.strip('"')
                ua[key] = value
        return ua

def file_read_E():
    """
    Зчитує англійські переклади з файлу та повертає їх у вигляді словника.
    """
    with open('Files/translations_en', 'r', encoding='utf-8') as file:
        en = {}
        for line in file:
            line = line.strip()
            if ": " in line:
                key, value = line.split(": ", 1)
                key = key.strip('"')
                value = value.strip('"')
                en[key] = value
        return en