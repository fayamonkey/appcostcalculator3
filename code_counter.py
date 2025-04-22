import os
import re
import pandas as pd
from pathlib import Path

# Dateitypen, die als Code betrachtet werden
CODE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.jsx': 'React',
    '.ts': 'TypeScript',
    '.tsx': 'React TypeScript',
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.java': 'Java',
    '.c': 'C',
    '.cpp': 'C++',
    '.h': 'C/C++ Header',
    '.cs': 'C#',
    '.php': 'PHP',
    '.rb': 'Ruby',
    '.go': 'Go',
    '.rs': 'Rust',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.dart': 'Dart',
    '.sql': 'SQL',
    '.sh': 'Shell',
    '.bat': 'Batch',
    '.ps1': 'PowerShell',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.json': 'JSON',
    '.md': 'Markdown',
    '.xml': 'XML',
    '.vue': 'Vue',
    '.scala': 'Scala',
    '.m': 'Objective-C',
    '.mm': 'Objective-C++',
    '.r': 'R',
}

# Kommentarmuster für verschiedene Sprachen
COMMENT_PATTERNS = {
    # Single-line comment patterns
    'single': {
        'py': r'#.*?$',
        'js|jsx|ts|tsx|java|c|cpp|cs|go|rs|swift|kt|dart|scala': r'//.*?$',
        'html|xml': r'<!--.*?-->',
        'sql': r'--.*?$',
        'rb': r'#.*?$',
    },
    # Multi-line comment patterns
    'multi': {
        'py': r'""".*?"""|\'\'\'.*?\'\'\'',
        'js|jsx|ts|tsx|java|c|cpp|cs|go|rs|swift|kt|dart|scala': r'/\*.*?\*/',
        'html|xml': r'<!--.*?-->',
    }
}

def get_language_from_extension(file_ext):
    """Gibt die Sprache basierend auf der Dateierweiterung zurück."""
    return CODE_EXTENSIONS.get(file_ext.lower(), "Other")

def is_binary_file(file_path):
    """Prüft, ob eine Datei binär ist."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file.read(1024)
            return False
    except UnicodeDecodeError:
        return True
    except Exception:
        return True

def count_lines_in_file(file_path):
    """
    Zählt die Anzahl der Zeilen in einer Datei, wobei leere Zeilen und Kommentare gesondert gezählt werden.
    """
    try:
        if is_binary_file(file_path):
            return 0, 0, 0
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        # Dateiendung ermitteln
        file_ext = os.path.splitext(file_path)[1].lower()
        language = get_language_from_extension(file_ext)
        
        # Alle Zeilen zählen
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Leere Zeilen zählen
        empty_lines = sum(1 for line in lines if not line.strip())
        
        # Kommentare entfernen, um Code-Zeilen zu zählen
        # Einfache Zuordnung von Dateierweiterungen zu Kommentarmustern
        comment_pattern = None
        
        # Single-line Kommentare
        for pattern_exts, pattern in COMMENT_PATTERNS['single'].items():
            if any(ext == file_ext.lstrip('.') for ext in pattern_exts.split('|')):
                content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        # Multi-line Kommentare
        for pattern_exts, pattern in COMMENT_PATTERNS['multi'].items():
            if any(ext == file_ext.lstrip('.') for ext in pattern_exts.split('|')):
                content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Verbleibende nicht-leere Zeilen zählen
        remaining_lines = content.split('\n')
        code_lines = sum(1 for line in remaining_lines if line.strip())
        
        return total_lines, empty_lines, code_lines
        
    except Exception as e:
        print(f"Fehler beim Zählen der Zeilen in {file_path}: {str(e)}")
        return 0, 0, 0

def count_lines_in_directory(directory_path, exclude_dirs=None):
    """
    Zählt die Anzahl der Zeilen in allen Dateien eines Verzeichnisses.
    
    Args:
        directory_path: Pfad zum zu analysierenden Verzeichnis
        exclude_dirs: Liste von Verzeichnisnamen, die ausgeschlossen werden sollen
        
    Returns:
        DataFrame mit Zeilenzahlen pro Datei und Gesamtstatistik
    """
    if exclude_dirs is None:
        exclude_dirs = ['node_modules', 'venv', '.git', '__pycache__']
    
    results = []
    total_lines = 0
    total_empty_lines = 0
    total_code_lines = 0
    total_files = 0
    lines_by_extension = {}
    
    try:
        for root, dirs, files in os.walk(directory_path):
            # Ausgeschlossene Verzeichnisse überspringen
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1]
                
                # Nur bekannte Code-Dateien analysieren
                if file_ext.lower() in CODE_EXTENSIONS:
                    file_lines, file_empty_lines, file_code_lines = count_lines_in_file(file_path)
                    
                    if file_lines > 0:
                        rel_path = os.path.relpath(file_path, directory_path)
                        language = get_language_from_extension(file_ext)
                        
                        results.append({
                            'file_path': rel_path,
                            'language': language,
                            'extension': file_ext,
                            'total_lines': file_lines,
                            'empty_lines': file_empty_lines,
                            'code_lines': file_code_lines,
                        })
                        
                        total_lines += file_lines
                        total_empty_lines += file_empty_lines
                        total_code_lines += file_code_lines
                        total_files += 1
                        
                        # Zeilen nach Dateityp aggregieren
                        if file_ext.lower() in lines_by_extension:
                            lines_by_extension[file_ext.lower()] += file_code_lines
                        else:
                            lines_by_extension[file_ext.lower()] = file_code_lines
        
        # DataFrame mit den Ergebnissen erstellen
        results_df = pd.DataFrame(results)
        
        # Zusammenfassung der Statistik
        stats = {
            'total_lines': total_lines,
            'total_empty_lines': total_empty_lines,
            'total_code_lines': total_code_lines,
            'total_files': total_files,
            'lines_by_extension': lines_by_extension
        }
        
        return results_df, stats
    
    except Exception as e:
        print(f"Fehler bei der Verzeichnisanalyse: {str(e)}")
        # Leere Ergebnisse zurückgeben
        return pd.DataFrame(), {
            'total_lines': 0,
            'total_empty_lines': 0,
            'total_code_lines': 0,
            'total_files': 0,
            'lines_by_extension': {}
        }

def estimate_effort_and_cost(total_code_lines, team_size, dev_monthly_salary):
    """
    Schätzt den Entwicklungsaufwand in Personenmonaten und die Kosten.
    
    Args:
        total_code_lines: Gesamtanzahl der Code-Zeilen
        team_size: Anzahl der Entwickler im Team
        dev_monthly_salary: Durchschnittliches Monatsgehalt eines Entwicklers in Euro
        
    Returns:
        Tuple mit (effort_months, total_cost)
    """
    # Produktivitätsraten basierend auf Projektgröße (Code-Zeilen pro Entwickler pro Tag)
    if total_code_lines < 5000:
        # Kleine Projekte: höhere Produktivität
        lines_per_dev_per_day = 150
    elif total_code_lines < 50000:
        # Mittlere Projekte: mittlere Produktivität
        lines_per_dev_per_day = 100
    else:
        # Große Projekte: niedrigere Produktivität
        lines_per_dev_per_day = 80
    
    # Arbeitstage pro Monat
    work_days_per_month = 21
    
    # Produktive Zeit pro Tag (in Prozent) - berücksichtigt Meetings, Planung, etc.
    productive_time_percentage = 0.7
    
    # Zeilen pro Entwickler pro Monat
    lines_per_dev_per_month = lines_per_dev_per_day * work_days_per_month * productive_time_percentage
    
    # Gesamte Personenmonate
    effort_months = total_code_lines / lines_per_dev_per_month
    
    # Kalenderzeit in Monaten (dividiert durch Teamgröße)
    calendar_months = effort_months / team_size
    
    # Teameffizienz-Faktor (größere Teams haben mehr Overhead)
    if team_size <= 2:
        efficiency_factor = 1.0
    elif team_size <= 5:
        efficiency_factor = 0.9
    else:
        efficiency_factor = 0.8
    
    # Angepasste Kalenderzeit
    calendar_months = calendar_months / efficiency_factor
    
    # Gesamtkosten (Teamgröße * Monate * Monatsgehalt)
    total_cost = team_size * calendar_months * dev_monthly_salary
    
    return calendar_months, total_cost 