import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import zipfile
import tempfile
import io
import shutil
from code_counter import count_lines_in_directory, estimate_effort_and_cost

# Gemeinsame Funktion zur Anzeige der Analyseergebnisse
def display_analysis_results(result_df, stats, effort_months, cost):
    # Zeige Gesamtstatistik
    st.markdown("""
    <div style="background-color: #F0F9FF; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0; border-left: 5px solid #0EA5E9;">
        <h3 style="color: #0369A1; margin-top: 0; font-size: 1.3rem;">📊 Projektübersicht</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Metriken in Karten mit verbesserten Styling
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.markdown(f"""
        <div style="background-color: white; padding: 1.2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 100%;">
            <h4 style="color: #4B5563; font-size: 0.9rem; margin-bottom: 0.5rem;">ANZAHL DATEIEN</h4>
            <p style="color: #1E40AF; font-size: 2rem; font-weight: 700; margin: 0;">{stats['total_files']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background-color: white; padding: 1.2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 1rem;">
            <h4 style="color: #4B5563; font-size: 0.9rem; margin-bottom: 0.5rem;">CODE-ZEILEN</h4>
            <p style="color: #1E40AF; font-size: 2rem; font-weight: 700; margin: 0;">{stats['total_code_lines']:,}</p>
            <p style="color: #6B7280; font-size: 0.8rem; margin: 0;">ohne Leerzeilen/Kommentare</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_stats2:
        st.markdown(f"""
        <div style="background-color: white; padding: 1.2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 100%;">
            <h4 style="color: #4B5563; font-size: 0.9rem; margin-bottom: 0.5rem;">GESAMTZEILEN</h4>
            <p style="color: #1E40AF; font-size: 2rem; font-weight: 700; margin: 0;">{stats['total_lines']:,}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background-color: white; padding: 1.2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 1rem;">
            <h4 style="color: #4B5563; font-size: 0.9rem; margin-bottom: 0.5rem;">GESCHÄTZTER AUFWAND</h4>
            <p style="color: #1E40AF; font-size: 2rem; font-weight: 700; margin: 0;">{effort_months:.1f}</p>
            <p style="color: #6B7280; font-size: 0.8rem; margin: 0;">Personenmonate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_stats3:
        st.markdown(f"""
        <div style="background-color: white; padding: 1.2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 100%;">
            <h4 style="color: #4B5563; font-size: 0.9rem; margin-bottom: 0.5rem;">DATEITYPEN</h4>
            <p style="color: #1E40AF; font-size: 2rem; font-weight: 700; margin: 0;">{len(stats['lines_by_extension'])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background-color: white; padding: 1.2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 1rem;">
            <h4 style="color: #4B5563; font-size: 0.9rem; margin-bottom: 0.5rem;">GESCHÄTZTE KOSTEN</h4>
            <p style="color: #1E40AF; font-size: 2rem; font-weight: 700; margin: 0;">{cost:,.2f} €</p>
            <p style="color: #6B7280; font-size: 0.8rem; margin: 0;">Gesamtkosten</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Visualisierungen
    st.markdown("""
    <div style="background-color: #ECFDF5; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0; border-left: 5px solid #10B981;">
        <h3 style="color: #065F46; margin-top: 0; font-size: 1.3rem;">📈 Visualisierungen</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        # Kuchendiagramm für Dateitypen
        ext_df = pd.DataFrame(list(stats['lines_by_extension'].items()), 
                            columns=['Dateityp', 'Anzahl Zeilen'])
        ext_df = ext_df.sort_values('Anzahl Zeilen', ascending=False)
        
        colors = px.colors.qualitative.Bold
        
        fig1 = px.pie(ext_df, names='Dateityp', values='Anzahl Zeilen',
                    title='<b>Verteilung der Code-Zeilen nach Dateityp</b>',
                    color_discrete_sequence=colors)
        
        fig1.update_layout(
            font=dict(family="Arial, sans-serif"),
            title_font=dict(size=18, color="#1E3A8A"),
            legend_title_font=dict(size=14),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=50, b=100, l=10, r=10)
        )
        
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_viz2:
        # Balkendiagramm für die größten Dateien
        top_files = result_df.sort_values('code_lines', ascending=False).head(10)
        
        fig2 = px.bar(top_files, x='code_lines', y='file_path', 
                    title='<b>Top 10 Dateien nach Code-Zeilen</b>',
                    labels={'code_lines': 'Anzahl Code-Zeilen', 'file_path': 'Dateipfad'},
                    color='code_lines',
                    color_continuous_scale='blues',
                    text='code_lines')
        
        fig2.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            font=dict(family="Arial, sans-serif"),
            title_font=dict(size=18, color="#1E3A8A"),
            hoverlabel=dict(bgcolor="white", font_size=12),
            height=450,
            margin=dict(t=50, b=50, l=10, r=10)
        )
        
        fig2.update_traces(texttemplate='%{text}', textposition='outside')
        
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detaillierte Dateiliste
    st.markdown("""
    <div style="background-color: #EFF6FF; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0; border-left: 5px solid #3B82F6;">
        <h3 style="color: #1E40AF; margin-top: 0; font-size: 1.3rem;">📁 Detaillierte Dateiliste</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Verbesserte Datentabelle
    st.markdown('<div style="background-color: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    st.dataframe(
        result_df.sort_values('code_lines', ascending=False), 
        use_container_width=True,
        column_config={
            "file_path": st.column_config.TextColumn("Dateipfad"),
            "language": st.column_config.TextColumn("Sprache"),
            "extension": st.column_config.TextColumn("Erweiterung"),
            "total_lines": st.column_config.NumberColumn("Gesamtzeilen"),
            "empty_lines": st.column_config.NumberColumn("Leerzeilen"),
            "code_lines": st.column_config.NumberColumn("Code-Zeilen"),
        }
    )
    st.markdown('</div>', unsafe_allow_html=True)

# App-Konfiguration mit angepasstem Design
st.set_page_config(
    page_title="App Coding & Entwicklungs-Kostenkalkulator",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS für ein professionelleres Aussehen
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    h1 {
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    h2, h3 {
        color: #2563EB;
        font-weight: 600;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1E40AF;
    }
    .stMetric {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stMetric label {
        color: #4B5563;
        font-weight: 500;
    }
    .stMetric .metric-value {
        font-weight: 700;
        color: #1E3A8A;
    }
    .css-1544g2n {
        padding: 2rem 1rem;
    }
    .plot-container {
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        background-color: white;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Titel und Einführung
st.title("App Coding & Entwicklungs-Kostenkalkulator")

st.markdown("""
<div style="background-color: #EFF6FF; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; border-left: 5px solid #2563EB;">
<h4 style="color: #1E3A8A; margin-top: 0;">Diese App analysiert Ihre Codebasis, zählt Zeilen pro Datei und Dateityp und schätzt den Entwicklungsaufwand.</h4>

<p><strong>Anleitung:</strong></p>
<ol>
    <li>Laden Sie ein Verzeichnis hoch oder geben Sie einen Pfad ein</li>
    <li>Stellen Sie bei Bedarf die Parameter für die Aufwandsschätzung ein</li>
    <li>Erhalten Sie detaillierte Statistiken über Ihre Codebasis</li>
</ol>
</div>
""", unsafe_allow_html=True)

# Tabs mit verbesserten UI-Elementen
tab1, tab2 = st.tabs(["🔍 Analyse", "ℹ️ Über das Tool"])

with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div style="background-color: #F8FAFC; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <h3 style="color: #2563EB; margin-top: 0; font-size: 1.2rem;">⚙️ Einstellungen</h3>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader("Verzeichnis hochladen (ZIP-Datei)", type=["zip"], accept_multiple_files=False)
        
        directory_path = st.text_input("ODER Verzeichnispfad eingeben (lokal)", 
                                     placeholder="z.B. C:/MeinProjekt",
                                     help="Geben Sie den absoluten Pfad zu Ihrem Projektverzeichnis ein")
        
        st.markdown("""
        <div style="background-color: #F8FAFC; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0;">
            <h3 style="color: #2563EB; margin-top: 0; font-size: 1.2rem;">💰 Parameter für Kostenberechnung</h3>
        </div>
        """, unsafe_allow_html=True)
        
        dev_salary = st.number_input("Durchschnittliches Monatsgehalt eines Entwicklers (€)", 
                                   min_value=1000, 
                                   value=8000, 
                                   step=500,
                                   help="Brutto-Monatsgehalt eines durchschnittlichen Entwicklers in Ihrem Team")
        
        team_size = st.number_input("Teamgröße (Anzahl der Entwickler)", 
                                  min_value=1, 
                                  value=3, 
                                  step=1,
                                  help="Anzahl der Entwickler, die an diesem Projekt arbeiten würden")
        
        exclude_dirs = st.text_input("Verzeichnisse ausschließen (kommagetrennt)", 
                                   value="node_modules,venv,.git,__pycache__",
                                   help="Diese Verzeichnisse werden bei der Analyse übersprungen")
        
        exclude_dirs = [d.strip() for d in exclude_dirs.split(",") if d.strip()]
        
        analyze_button = st.button("Analysieren", type="primary")
    
    with col2:
        if analyze_button and (uploaded_files or directory_path):
            # Verarbeitung der hochgeladenen ZIP-Datei
            if uploaded_files:
                with st.spinner('Entpacke ZIP-Datei und analysiere Codebasis... Bitte warten.'):
                    try:
                        # Debugging-Ausgabe
                        st.write(f"Verarbeite hochgeladene Datei: {uploaded_files.name}, Größe: {uploaded_files.size} bytes")
                        
                        # Temporäres Verzeichnis erstellen
                        temp_dir = tempfile.mkdtemp()
                        st.write(f"Temporäres Verzeichnis erstellt: {temp_dir}")
                        
                        try:
                            # ZIP-Datei in das temporäre Verzeichnis extrahieren
                            with zipfile.ZipFile(uploaded_files, 'r') as zip_ref:
                                # Liste aller Dateien in der ZIP anzeigen
                                file_list = zip_ref.namelist()
                                st.write(f"Anzahl der Dateien in ZIP: {len(file_list)}")
                                if len(file_list) > 0:
                                    st.write(f"Beispieldateien: {file_list[:5]}")
                                
                                # Extrahieren
                                zip_ref.extractall(temp_dir)
                                st.write(f"Dateien wurden nach {temp_dir} extrahiert")
                            
                            # Überprüfen, ob Dateien extrahiert wurden
                            extracted_files = os.listdir(temp_dir)
                            st.write(f"Extrahierte Dateien: {len(extracted_files)} Dateien/Verzeichnisse gefunden")
                            if len(extracted_files) > 0:
                                st.write(f"Beispiel extrahierte Dateien/Verzeichnisse: {extracted_files[:5]}")
                            
                            # Analyse durchführen
                            result_df, stats = count_lines_in_directory(temp_dir, exclude_dirs)
                            
                            # Aufwandsschätzung
                            effort_months, cost = estimate_effort_and_cost(stats['total_code_lines'], team_size, dev_salary)
                            
                            # Gemeinsame Funktion zur Anzeige der Analyseergebnisse
                            display_analysis_results(result_df, stats, effort_months, cost)
                            
                            # Temporäres Verzeichnis bereinigen
                            try:
                                if os.path.exists(temp_dir):
                                    shutil.rmtree(temp_dir)
                                    st.write("Temporäres Verzeichnis wurde bereinigt.")
                            except Exception as cleanup_error:
                                st.warning(f"Hinweis: Konnte temporäres Verzeichnis nicht bereinigen: {str(cleanup_error)}")
                            
                        except Exception as e:
                            st.markdown(f"""
                            <div style="background-color: #FEE2E2; color: #B91C1C; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
                                <h4 style="margin-top: 0;">⚠️ Fehler bei der Analyse</h4>
                                <p>Fehler bei der Verarbeitung der ZIP-Datei: {str(e)}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            # Temporäres Verzeichnis bereinigen
                            if os.path.exists(temp_dir):
                                shutil.rmtree(temp_dir)
                            st.stop()
                    
                    except Exception as e:
                        st.markdown(f"""
                        <div style="background-color: #FEE2E2; color: #B91C1C; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
                            <h4 style="margin-top: 0;">⚠️ Fehler bei der Analyse</h4>
                            <p>{str(e)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.stop()
            
            # Verwendung des eingegebenen Verzeichnispfads
            elif directory_path:
                with st.spinner('Analysiere Codebasis... Bitte warten.'):
                    try:
                        result_df, stats = count_lines_in_directory(directory_path, exclude_dirs)
                        
                        # Aufwandsschätzung
                        effort_months, cost = estimate_effort_and_cost(stats['total_code_lines'], team_size, dev_salary)
                        
                        # Gemeinsame Funktion zur Anzeige der Analyseergebnisse
                        display_analysis_results(result_df, stats, effort_months, cost)
                    
                    except Exception as e:
                        st.markdown(f"""
                        <div style="background-color: #FEE2E2; color: #B91C1C; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
                            <h4 style="margin-top: 0;">⚠️ Fehler bei der Analyse</h4>
                            <p>{str(e)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.stop()
            else:
                # Info-Nachricht anzeigen, wenn keine Analyse erfolgt ist
                st.markdown("""
                <div style="background-color: #F0F9FF; padding: 2rem; border-radius: 8px; margin-top: 3rem; text-align: center; border: 1px dashed #0EA5E9;">
                    <img src="https://cdn-icons-png.flaticon.com/512/7069/7069922.png" width="80" style="margin-bottom: 1rem;">
                    <h3 style="margin-top: 0; color: #0369A1;">Bereit zum Analysieren!</h3>
                    <p style="color: #0284C7;">Laden Sie eine ZIP-Datei hoch oder geben Sie einen Verzeichnispfad ein, um Ihre Codebasis zu evaluieren.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Info-Nachricht anzeigen, wenn keine Analyse erfolgt ist
            st.markdown("""
            <div style="background-color: #F0F9FF; padding: 2rem; border-radius: 8px; margin-top: 3rem; text-align: center; border: 1px dashed #0EA5E9;">
                <img src="https://cdn-icons-png.flaticon.com/512/7069/7069922.png" width="80" style="margin-bottom: 1rem;">
                <h3 style="margin-top: 0; color: #0369A1;">Bereit zum Analysieren!</h3>
                <p style="color: #0284C7;">Laden Sie eine ZIP-Datei hoch oder geben Sie einen Verzeichnispfad ein, um Ihre Codebasis zu evaluieren.</p>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div style="background-color: #F8FAFC; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h2 style="color: #1E40AF; margin-top: 0;">💡 App Coding & Entwicklungs-Kostenkalkulator</h2>
        
        <p>Dieses Tool hilft dabei, den Umfang und Aufwand von Softwareprojekten zu quantifizieren. Es bietet:</p>
        
        <div style="margin: 1.5rem 0;">
            <div style="display: flex; align-items: flex-start; margin-bottom: 1rem;">
                <div style="background-color: #DBEAFE; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; flex-shrink: 0;">
                    <span style="color: #1E40AF; font-weight: bold;">1</span>
                </div>
                <div>
                    <h4 style="margin: 0; color: #1E40AF;">Zeilenanalyse</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #4B5563;">Zählt Code-Zeilen (ohne Leerzeilen und Kommentare)</p>
                </div>
            </div>
            
            <div style="display: flex; align-items: flex-start; margin-bottom: 1rem;">
                <div style="background-color: #DBEAFE; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; flex-shrink: 0;">
                    <span style="color: #1E40AF; font-weight: bold;">2</span>
                </div>
                <div>
                    <h4 style="margin: 0; color: #1E40AF;">Aufwandsschätzung</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #4B5563;">Berechnet den geschätzten Entwicklungsaufwand in Personenmonaten</p>
                </div>
            </div>
            
            <div style="display: flex; align-items: flex-start; margin-bottom: 1rem;">
                <div style="background-color: #DBEAFE; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; flex-shrink: 0;">
                    <span style="color: #1E40AF; font-weight: bold;">3</span>
                </div>
                <div>
                    <h4 style="margin: 0; color: #1E40AF;">Kostenabschätzung</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #4B5563;">Schätzt die Entwicklungskosten basierend auf Teamgröße und Gehältern</p>
                </div>
            </div>
        </div>
    </div>
    
    <div style="background-color: #F8FAFC; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h3 style="color: #1E40AF; margin-top: 0;">🧮 Berechnungsmethodik</h3>
        
        <p>Die Aufwandsschätzung basiert auf Branchenstandards und Erfahrungswerten:</p>
        
        <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin: 1.5rem 0;">
            <div style="flex: 1; min-width: 200px; background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #3B82F6;">
                <h4 style="margin-top: 0; color: #2563EB;">Kleine Projekte</h4>
                <p style="color: #4B5563; font-size: 0.9rem;">< 5.000 Zeilen Code</p>
                <p style="font-weight: 600; color: #1E40AF; font-size: 1.2rem;">~150 Zeilen/Tag</p>
                <p style="color: #6B7280; font-size: 0.8rem;">pro Entwickler</p>
            </div>
            
            <div style="flex: 1; min-width: 200px; background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #6366F1;">
                <h4 style="margin-top: 0; color: #4F46E5;">Mittlere Projekte</h4>
                <p style="color: #4B5563; font-size: 0.9rem;">5.000-50.000 Zeilen Code</p>
                <p style="font-weight: 600; color: #1E40AF; font-size: 1.2rem;">~100 Zeilen/Tag</p>
                <p style="color: #6B7280; font-size: 0.8rem;">pro Entwickler</p>
            </div>
            
            <div style="flex: 1; min-width: 200px; background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #8B5CF6;">
                <h4 style="margin-top: 0; color: #7C3AED;">Große Projekte</h4>
                <p style="color: #4B5563; font-size: 0.9rem;">> 50.000 Zeilen Code</p>
                <p style="font-weight: 600; color: #1E40AF; font-size: 1.2rem;">~80 Zeilen/Tag</p>
                <p style="color: #6B7280; font-size: 0.8rem;">pro Entwickler</p>
            </div>
        </div>
        
        <p>Diese Werte berücksichtigen nicht nur das reine Codieren, sondern auch Planung, Design, Dokumentation, Tests und Fehlerbehebung.</p>
    </div>
    
    <div style="background-color: #F8FAFC; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h3 style="color: #1E40AF; margin-top: 0;">⚠️ Einschränkungen</h3>
        
        <ul style="color: #4B5563; margin-left: 1.5rem;">
            <li style="margin-bottom: 0.5rem;">Die Schätzungen sind Annäherungen und können je nach Projektart, Komplexität und Teamerfahrung variieren</li>
            <li style="margin-bottom: 0.5rem;">Das Tool unterscheidet nicht zwischen verschiedenen Komplexitätsgraden von Code</li>
            <li style="margin-bottom: 0.5rem;">Automatisch generierter Code wird genauso gewertet wie manuell geschriebener Code</li>
        </ul>
    </div>
    
    <div style="background-color: #F8FAFC; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;">
        <h3 style="color: #1E40AF; margin-top: 0;">💻 Entwickelt mit</h3>
        
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 1rem;">
            <div style="text-align: center; min-width: 100px;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1869px-Python-logo-notext.svg.png" width="50" style="margin-bottom: 0.5rem;">
                <p style="margin: 0; font-weight: 600; color: #1E3A8A;">Python</p>
            </div>
            <div style="text-align: center; min-width: 100px;">
                <img src="https://streamlit.io/images/brand/streamlit-mark-color.png" width="50" style="margin-bottom: 0.5rem;">
                <p style="margin: 0; font-weight: 600; color: #1E3A8A;">Streamlit</p>
            </div>
            <div style="text-align: center; min-width: 100px;">
                <img src="https://pandas.pydata.org/static/img/pandas_mark.svg" width="50" style="margin-bottom: 0.5rem;">
                <p style="margin: 0; font-weight: 600; color: #1E3A8A;">Pandas</p>
            </div>
            <div style="text-align: center; min-width: 100px;">
                <img src="https://plotly.com/all_static/images/icon-dash.png" width="50" style="margin-bottom: 0.5rem;">
                <p style="margin: 0; font-weight: 600; color: #1E3A8A;">Plotly</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True) 