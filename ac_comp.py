import os
import zipfile
import tempfile
from io import BytesIO
from typing import List, Dict, TypedDict, Annotated
import operator
import datetime # Import for timestamps
import requests
import re
import time # Import for simulating UI update delays

from requests.auth import HTTPBasicAuth

import streamlit as st
from docx import Document
from langgraph.graph import StateGraph, END
from langchain_tcs_bfsi_genai import APIClient, Auth, TCSChatModel, TCSEmbeddings, TCSLLMs # Added TCSLLMs for the new agent

import pandas as pd
import json
import numpy as np
import textwrap
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.messages import AIMessageChunk, BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from streamlit_lottie import st_lottie
# Imports for the new agent
import yaml
import re
from collections import defaultdict

#from utillty_functions.utils import get_query_params
# --- Language Translation Dictionary ---
translations = {
    "en": {
        "title": "✨ Automated Incident Management Pipeline ✨",
        "credits": "Credits: <em><a href='https://ismartams.tcsapps.com/#/'>iSmart</a></em>",
        "info_text": "This workflow systematically ingests incident tickets, parses event metadata, assigns appropriate Subject Matter Experts (SMEs), dynamically adjusts priority according to impacts and dependencies, and conducts real-time log correlation for root cause analysis. It also identifies potential solutions, initiates automated remediation scripts, and updates ticket status throughout each stage to ensure thorough and comprehensive issue resolution.",
        "run_pipeline_button": "🚀 Run Incident Automation Pipeline",
        "decision_required": "Decision Required",
        "self_healing": "Self Healing",
        "manual_intervention": "Manual Intervention",
        "submit_button": "Submit",
        "pipeline_complete": "🎊✨ Pipeline Complete! ✨🎊",
        "final_outcome": "✨ Full Final Pipeline Outcome:",
        "log_expander": "Click to view detailed logs",
        "run_pipeline": "Starting Incident Automation Pipeline...",
        "agent1_title": "🕵️‍♂️ Incident Details & Validation Output",
        "agent2_title": "👨‍💻 Ticket Assignment Result",
        "agent3_title": "📈 Application Impact Analysis & Ticket Priority Update",
        "agent4_title": "🔎 Log Analysis & Resolution Recommendations",
        "agent5_title": "🩹 Self-Healing & Ticket Closure",
        "agent6_title": "🩹 Manual Intervention",
        "problem_record_title": "🩹 Problem Record Generator",
        "error_message": "❌ **ERROR:**",
        "success_message": "✅",
        "info_message": "ℹ️",
        "warning_message": "⚠️",
        "data_quality_passed": "✅ Data Quality Check: **PASSED**",
        "data_quality_failed": "❌ Data Quality Check: **FAILED** -",
        "view_full_desc": "📄 View Full Description",
        "no_incidents_found": "No incidents found or an error occurred during fetch.",
        "desc_incomplete": "description incomplete. Pipeline stopped.",
        "desc_ok": "description is OK.",
        "error_no_incident": "Error: No incident available in state for assignment.",
        "error_no_sysid": "Error: No sys_id found for incident",
        "assignment_finished": "Ticket assignment process finished for",
        "priority_update_title": "📈 Application Impact Analysis & Ticket Priority Update",
        "iadd_summary": "🗺️ <em><a href='https://ismartams.tcsapps.com/#/iadd'>IADD</em> Analysis Summary : </strong></a>",
        "priority_not_updated": "Priority not updated for",
        "priority_updated": "Priority update for",
        "log_analysis_title": "🔎 Log Analysis & Resolution Recommendations",
        "log_preview": "🔍 Log Preview:",
        "view_full_log": "📖 View Full Log File",
        "no_logs_found": "✅ No errors found in the log file. No specific resolution recommended based on logs.",
        "error_summary": "🪵 Extracted Error Summary:",
        "checking_sop": "📘 Checking SOP for each issue...",
        "error_type": "🔍 **Error Type:**",
        "sop_found": "✅ **SOP Found:**",
        "resolution_steps": "🛠️   **Resolution Steps:**",
        "strategic_recommendation": "🧠 Strategic Recommendation:",
        "self_healing_title": "🩹 Self-Healing & Ticket Closure",
        "health_check_title": "🩹 Health Check Monitoring",
        "manual_intervention_required": "Human intervention is required. Please refer to the recommended resolution steps above and proceed manually.",
        "feedback_prompt": "Enter your feedback:",
        "feedback_placeholder": "Type something...",
        "feedback_submitted": "Feedback submitted successfully",
        "enter_feedback": "Please enter some text before submitting.",
        "pipeline_stopped": "Pipeline stopped early. 🛑",
        "reason_for_stop": "**Reason for Stop:**",
        "incident_involved": "The incident involved was: **",
        "no_further_agents": "No further agents were executed due to the conditional check.",
        "successfully_processed": "Incident ** successfully processed. 🎉",
        "final_assignment_status": "**Final Assignment Status:**",
        "priority_update_status": "**Priority Update Status:**",
        "recommended_resolution": "**Recommended Resolution (from Log Analysis):**",
        "self_healing_closure_status": "**Self-Healing & Closure Status:**",
        "manual_intervention_required_text": "Manual Intervention Required to update the ticket",
        "manual_feedback_submitted": "Manual Feedback submitted",
        "full_execution_log": "📜 Full Execution Log:",
        "progress_text": "Progress: {percent}%",
        "choose_language": "Choose Language",
        "english": "English",
        "spanish": "Español",
        "portuguese": "Português",
        "incident_number": "Incident Number: ",
        "incident_description": "Incident Description: ",
        "agent": "Agent",
        "inc_description": "Ismart user authentication issue, not able to use DHAC , IRR. Multiple application impacted",
        "assignment_desription": "The assignment was determined based on a combination of historical resolution efficiency, current workload distribution and the active support roster. Mr. Suvomoy Nandy has been identified as the most appropriate resource to address this incident, ensuring minimal resolution time and optimal resource utilization.",
        "analysis_summary_info": "The affected component is a source dependency for two Gold-tier applications, both of which support real-time transactional workloads.",
        "analysis_disclaimer": "🚨 According to AMS prioritization logic, any failure impacting greater than or equals to Two Gold applications, warrants a Priority 2 classification",
        "analysis_warning": "📈 This incident has therefore been flagged for accelerated resolution to prevent SLA breaches and downstream user disruptions.",
        "connect_linux": "🔍 Connecting to Linux server...",
        "authenticate_server": "🔐 Authenticating with server ID and password...",
        "fetch_logs": "📁 Fetching logs from system path: `/var/logs/app/ARE_application_logs.log`",
        "file_found": "📄 Log file found. Reading now...\n",
        "no_error": "No errors found in application logs, no specific resolution recommended based on logs.",
        "self_heal": "🛠️   Initiating self-healing for:",
        "spinner_self_heal": "Running Self Healing... Please wait.",
        "oracle_connect": "🔌 Connecting to Oracle Database as SYSDBA...",
        "preparing_resolution": "📥 Preparing resolution queries...",
        "executing1": "🧾 Executing: `ALTER USER ISMART ACCOUNT UNLOCK;`",
        "executing2": "🧾 Executing: `ALTER USER ISMART IDENTIFIED BY ismart123;`",
        "self_healing_simulation": "Self-healing simulation completed for: ",
        "executing_sop": "📄 Executing SOP-recommended queries...",
        "self_healing_sop": "Self-healing simulation completed based on SOP.",
        "updated_service_now": "📣 Going to update the ticket in ServiceNow...",
        "updated_success": "Ticket updated successfully in ServiceNow.",
        "failed_to_close": "❌ Failed to close ticket:",
        "health_check_spinner": "Running Health Check... Please wait.",
        "connection_string": "📄 Attempting connection using connection string:",
        "connection_successful": "✅ Successfully connected to the database in 2.5 seconds.",
        "select_query": "🔍 Health Check: Running SELECT query to verify account status...",
        "query1_executed": "✅ Query executed successfully in 1.5 seconds.",
        "select_count": "🔍 Health Check: Running SELECT COUNT query to verify account status...",
        "query2_executed": "✅ Query executed successfully in 1.2 seconds.",
        "completed": "🎉 ✅ Health Check Completed Successfully!",
        "generating_problem": "🔍 Generating Problem Record referring to the Root Cause Analysis...",
        "generating_record": "📝 Generating Record Description...",
        "connect_serviceNow": "🔗 Connecting to ServiceNow...",
        "register_problem": "📋 Registering Problem Record in ServiceNow...",
        "created_record": "Problem record created in ServiceNow! Number:",
        "failed_record": "Failed to create record. Status:",
        "details": "Details:",
        "incident_priority": "Incident Priority Setting is Done in ServiceNow with Priority :",
        "incident_assigned": "Incident assignment is done to",
        "serviceNow": "in ServiceNow",
        "incident_failed": "Incident update request failed:",
        "failed_update": "Failed to update ticket ",
        "proceed": "Please choose how to proceed.",
        "failed_priority": "Failed to update ticket priority",
        "log_fetch_splunk": "Fetching logs from Splunk",
        "fetching": "Running: Fetching and validating incident data...",
        "impact": "Running: Doing impact analysis and updating incident priority...",
        "assigning": "Running: Assigning the validated ticket...",
        "extraction": "Running: Log Extraction and Resolution Recommendation...",
        "choose": "Please go below to select how you wish to proceed..."
    },
    "es": {
        "title": "✨ Pipeline de Gestión Automatizada de Incidentes ✨",
        "credits": "Créditos: <em><a href='https://ismartams.tcsapps.com/#/'>iSmart</a></em>",
        "info_text": "Este flujo de trabajo ingresa de manera sistemática los tickets de incidentes, analiza los metadatos del evento, asigna Expertos en Asuntos Específicos (SMEs) adecuados, ajusta dinámicamente la prioridad según los impactos y dependencias, y realiza correlación en tiempo real de registros para el análisis de causa raíz. También identifica soluciones potenciales, inicia scripts de remediación automatizados y actualiza el estado del ticket en cada etapa para garantizar una resolución completa y exhaustiva.",
        "run_pipeline_button": "🚀 Ejecutar Pipeline de Automatización de Incidentes",
        "decision_required": "Requiere Decisión",
        "self_healing": "Autoconstrucción",
        "manual_intervention": "Intervención Manual",
        "submit_button": "Enviar",
        "pipeline_complete": "🎊✨ ¡Pipeline Completado! ✨🎊",
        "final_outcome": "✨ Resultado Final Completo del Pipeline:",
        "log_expander": "Haga clic para ver los registros detallados",
        "run_pipeline": "Iniciando Pipeline de Automatización de Incidentes...",
        "agent1_title": "🕵️‍♂️ Salida de Detalles del Incidente y Validación",
        "agent2_title": "👨‍💻 Resultado de Asignación del Ticket",
        "agent3_title": "📈 Análisis de Impacto de Aplicación y Actualización de Prioridad del Ticket",
        "agent4_title": "🔎 Análisis de Registros y Recomendaciones de Resolución",
        "agent5_title": "🩹 Autoconstrucción y Cierre del Ticket",
        "agent6_title": "🩹 Intervención Manual",
        "problem_record_title": "🩹 Generador de Registro de Problema",
        "error_message": "❌ **ERROR:**",
        "success_message": "✅",
        "info_message": "ℹ️",
        "warning_message": "⚠️",
        "data_quality_passed": "✅ Verificación de Calidad de Datos: **APROBADA**",
        "data_quality_failed": "❌ Verificación de Calidad de Datos: **FALLIDA** -",
        "view_full_desc": "📄 Ver Descripción Completa",
        "no_incidents_found": "No se encontraron incidentes o ocurrió un error durante la búsqueda.",
        "desc_incomplete": "descripción incompleta. Pipeline detenido.",
        "desc_ok": "descripción es correcta.",
        "error_no_incident": "Error: No hay incidente disponible en el estado para asignación.",
        "error_no_sysid": "Error: No se encontró sys_id para el incidente",
        "assignment_finished": "Proceso de asignación de ticket finalizado para",
        "priority_update_title": "📈 Análisis de Impacto de Aplicación y Actualización de Prioridad del Ticket",
        "iadd_summary": "🗺️ <em><a href='https://ismartams.tcsapps.com/#/iadd'>Resumen de Análisis IADD</em> : </strong></a>",
        "priority_not_updated": "Prioridad no actualizada para",
        "priority_updated": "Actualización de prioridad para",
        "log_analysis_title": "🔎 Análisis de Registros y Recomendaciones de Resolución",
        "log_preview": "🔍 Vista Previa de Registros:",
        "view_full_log": "📖 Ver Archivo Completo de Registros",
        "no_logs_found": "✅ No se encontraron errores en el archivo de registros. No se recomienda ninguna resolución específica basada en los registros.",
        "error_summary": "🪵 Resumen de Errores Extraídos:",
        "checking_sop": "📘 Verificando SOP para cada problema...",
        "error_type": "🔍 **Tipo de Error:**",
        "sop_found": "✅ **SOP Encontrado:**",
        "resolution_steps": "🛠️   **Pasos de Resolución:**",
        "strategic_recommendation": "🧠 Recomendación Estratégica:",
        "self_healing_title": "🩹 Autoconstrucción y Cierre del Ticket",
        "health_check_title": "🩹 Monitoreo de Verificación de Salud",
        "manual_intervention_required": "Se requiere intervención humana. Consulte los pasos de resolución recomendados anteriormente y proceda manualmente.",
        "feedback_prompt": "Ingrese sus comentarios:",
        "feedback_placeholder": "Escriba algo...",
        "feedback_submitted": "Comentarios enviados con éxito",
        "enter_feedback": "Por favor ingrese texto antes de enviar.",
        "pipeline_stopped": "Pipeline detenido prematuramente. 🛑",
        "reason_for_stop": "**Razón de la detención:**",
        "incident_involved": "El incidente involucrado fue: **",
        "no_further_agents": "No se ejecutaron más agentes debido a la verificación condicional.",
        "successfully_processed": "Incidente ** procesado con éxito. 🎉",
        "final_assignment_status": "**Estado Final de Asignación:**",
        "priority_update_status": "**Estado de Actualización de Prioridad:**",
        "recommended_resolution": "**Resolución Recomendada (del Análisis de Registros):**",
        "self_healing_closure_status": "**Estado de Autoconstrucción y Cierre:**",
        "manual_intervention_required_text": "Se requiere Intervención Manual para actualizar el ticket",
        "manual_feedback_submitted": "Comentarios Manuales Enviados",
        "full_execution_log": "📜 Registro Completo de Ejecución:",
        "progress_text": "Progreso: {percent}%",
        "choose_language": "Elegir Idioma",
        "english": "Inglés",
        "spanish": "Español",
        "portuguese": "Portugués",
        "incident_number": "Número de incidente: ",
        "incident_description": "Descripción del Incidente: ",
        "agent": "Agente",
        "inc_description": "Problema de autenticación de usuario de Ismart: no se puede usar DHAC ni IRR. Varias aplicaciones afectadas.",
        "assignment_desription": "La asignación se determinó con base en una combinación de la eficiencia histórica de resolución, la distribución actual de la carga de trabajo y la plantilla de soporte activa. El Sr. Suvomoy Nandy ha sido identificado como el recurso más adecuado para abordar este incidente, garantizando un tiempo de resolución mínimo y una utilización óptima de los recursos.",
        "analysis_summary_info": "El componente afectado es una dependencia de origen de dos aplicaciones de nivel Gold, las cuales admiten cargas de trabajo transaccionales en tiempo real.",
        "analysis_disclaimer": "🚨 Según la lógica de priorización de AMS, cualquier falla que afecte a más de dos aplicaciones Gold, garantiza una clasificación de Prioridad 2.",
        "analysis_warning": "📈 Por lo tanto, este incidente ha sido marcado para una resolución acelerada a fin de evitar violaciones del SLA y perturbaciones para los usuarios finales.",
        "connect_linux": "🔍 Conectando al servidor Linux...",
        "authenticate_server": "🔐 Autenticación con ID de servidor y contraseña...",
        "fetch_logs": "📁 Obteniendo registros de la ruta del sistema: `/var/logs/app/ARE_application_logs.log`",
        "file_found": "📄 Archivo de registro encontrado. Leyendo ahora...\n",
        "no_error": "No se encontraron errores en los registros de la aplicación; no se recomienda ninguna resolución específica según los registros.",
        "self_heal": "🛠️   Iniciando la autocuración para:",
        "spinner_self_heal": "Ejecutando autocuración... Por favor espere.",
        "oracle_connect": "🔌 Conectarse a la base de datos Oracle como SYSDBA...",
        "preparing_resolution": "📥 Preparando consultas de resolución....",
        "executing1": "🧾 Ejecutando: `ALTERAR USUARIO ISMART DESBLOQUEO DE CUENTA;`",
        "executing2": "🧾 Ejecutando: `ALTERAR USUARIO ISMART IDENTIFICADO POR ismart123;`",
        "self_healing_simulation": "Simulación de autocuración completada para: ",
        "executing_sop": "📄 Ejecutando consultas recomendadas por SOP...",
        "self_healing_sop": "Simulación de autocuración completada según SOP.",
        "updated_service_now": "📣 Voy a actualizar el ticket en ServiceNow...",
        "updated_success": "Ticket actualizado exitosamente en ServiceNow.",
        "failed_to_close": "❌ No se pudo cerrar el ticket:",
        "health_check_spinner": "Ejecutando control de salud... Por favor espere.",
        "connection_string": "📄 Intentando conexión usando cadena de conexión:",
        "connection_successful": "✅ Conectado exitosamente a la base de datos en 2,5 segundos.",
        "select_query": "🔍 Comprobación de estado: ejecución de la consulta SELECT para verificar el estado de la cuenta...",
        "query1_executed": "✅ Consulta ejecutada exitosamente en 1,5 segundos.",
        "select_count": "🔍 Comprobación de estado: ejecución de la consulta SELECT COUNT para verificar el estado de la cuenta...",
        "query2_executed": "✅ Consulta ejecutada exitosamente en 1,2 segundos.",
        "completed": "🎉 ✅ ¡Control de salud completado exitosamente!",
        "generating_problem": "🔍 Generando Registro de Problemas haciendo referencia al Análisis de Causa Raíz...",
        "generating_record": "📝 Generando descripción de registro...",
        "connect_serviceNow": "🔗 Conectándose a ServiceNow...",
        "register_problem": "📋 Registrando registro de problemas en ServiceNow...",
        "created_record": "Registro de problema creado en ServiceNow! Número:",
        "failed_record": "No se pudo crear el registro. Estado:",
        "details": "Detalles:",
        "incident_priority": "La configuración de la prioridad de incidentes se realiza en ServiceNow con Prioridad : ",
        "incident_assigned": "La asignación de incidentes se realiza a",
        "serviceNow": "en ServiceNow",
        "incident_failed": "Error en la solicitud de actualización de incidentes:",
        "failed_update": "No se pudo actualizar el ticket",
        "proceed": "Por favor, seleccione cómo proceder.",
        "failed_priority": "No se pudo actualizar la prioridad del ticket",
        "log_fetch_splunk": "Récupération des journaux de Splunk",
        "fetching": "Ejecución: Obteniendo y validando datos de incidentes...",
        "impact": "En ejecución: Realizar análisis de impacto y actualizar la prioridad de incidentes...",
        "assigning": "Ejecución: Asignando el ticket validado...",
        "extraction": "Ejecución: Recomendación de extracción y resolución de registros...",
        "choose": "Por favor, vaya a continuación para seleccionar cómo desea proceder..."
    },
    "pt": {
        "title": "✨ Pipeline de Gestão Automatizada de Incidentes ✨",
        "credits": "Créditos: <em><a href='https://ismartams.tcsapps.com/#/'>iSmart</a></em>",
        "info_text": "Este fluxo de trabalho coleta de forma sistemática os tickets de incidentes, analisa os metadados do evento, atribui Especialistas em Assuntos Específicos (SMEs) apropriados, ajusta dinamicamente a prioridade de acordo com os impactos e dependências, e realiza correlação em tempo real de logs para análise da causa raiz. Também identifica soluções potenciais, inicia scripts de remediação automatizados e atualiza o status do ticket em cada etapa para garantir uma resolução completa e abrangente.",
        "run_pipeline_button": "🚀 Executar Pipeline de Automação de Incidentes",
        "decision_required": "Decisão Necessária",
        "self_healing": "Auto-Recuperação",
        "manual_intervention": "Intervenção Manual",
        "submit_button": "Enviar",
        "pipeline_complete": "🎊✨ Pipeline Finalizado! ✨🎊",
        "final_outcome": "✨ Resultado Final Completo do Pipeline:",
        "log_expander": "Clique para ver os logs detalhados",
        "run_pipeline": "Iniciando Pipeline de Automação de Incidentes...",
        "agent1_title": "🕵️‍♂️ Saída de Detalhes do Incidente e Validação",
        "agent2_title": "👨‍💻 Resultado da Atribuição do Ticket",
        "agent3_title": "📈 Análise de Impacto da Aplicação e Atualização da Prioridade do Ticket",
        "agent4_title": "🔎 Análise de Logs e Recomendações de Resolução",
        "agent5_title": "🩹 Recuperação Automática e Encerramento do Ticket",
        "agent6_title": "🩹 Intervenção Manual",
        "problem_record_title": "🩹 Gerador de Registro de Problema",
        "error_message": "❌ **ERRO:**",
        "success_message": "✅",
        "info_message": "ℹ️",
        "warning_message": "⚠️",
        "data_quality_passed": "✅ Verificação de Qualidade de Dados: **APROVADA**",
        "data_quality_failed": "❌ Verificação de Qualidade de Dados: **FALHOU** -",
        "view_full_desc": "📄 Ver Descrição Completa",
        "no_incidents_found": "Nenhum incidente encontrado ou ocorreu um erro durante a busca.",
        "desc_incomplete": "descrição incompleta. Pipeline interrompido.",
        "desc_ok": "descrição está OK.",
        "error_no_incident": "Erro: Nenhum incidente disponível no estado para atribuição.",
        "error_no_sysid": "Erro: Nenhum sys_id encontrado para o incidente",
        "assignment_finished": "Processo de atribuição do ticket finalizado para",
        "priority_update_title": "📈 Análise de Impacto da Aplicação e Atualização da Prioridade do Ticket",
        "iadd_summary": "🗺️ <em><a href='https://ismartams.tcsapps.com/#/iadd'>Resumo da Análise IADD</em> : </strong></a>",
        "priority_not_updated": "Prioridade não atualizada para",
        "priority_updated": "Atualização de prioridade para",
        "log_analysis_title": "🔎 Análise de Logs e Recomendações de Resolução",
        "log_preview": "🔍 Visualização dos Logs:",
        "view_full_log": "📖 Ver Arquivo Completo de Logs",
        "no_logs_found": "✅ Nenhum erro encontrado no arquivo de logs. Nenhuma resolução específica recomendada com base nos logs.",
        "error_summary": "🪵 Resumo de Erros Extraídos:",
        "checking_sop": "📘 Verificando SOP para cada problema...",
        "error_type": "🔍 **Tipo de Erro:**",
        "sop_found": "✅ **SOP Encontrado:**",
        "resolution_steps": "🛠️   **Passos de Resolução:**",
        "strategic_recommendation": "🧠 Recomendação Estratégica:",
        "self_healing_title": "🩹 Recuperação Automática e Encerramento do Ticket",
        "health_check_title": "🩹 Monitoramento de Verificação de Saúde",
        "manual_intervention_required": "É necessária intervenção humana. Consulte os passos de resolução recomendados acima e prossiga manualmente.",
        "feedback_prompt": "Insira seus comentários:",
        "feedback_placeholder": "Digite algo...",
        "feedback_submitted": "Comentários enviados com sucesso",
        "enter_feedback": "Por favor insira algum texto antes de enviar.",
        "pipeline_stopped": "Pipeline interrompido prematuramente. 🛑",
        "reason_for_stop": "**Motivo da interrupção:**",
        "incident_involved": "O incidente envolvido foi: **",
        "no_further_agents": "Nenhum outro agente foi executado devido à verificação condicional.",
        "successfully_processed": "Incidente ** processado com sucesso. 🎉",
        "final_assignment_status": "**Status Final de Atribuição:**",
        "priority_update_status": "**Status de Atualização de Prioridade:**",
        "recommended_resolution": "**Resolução Recomendada (da Análise de Logs):**",
        "self_healing_closure_status": "**Status de Recuperação Automática e Encerramento:**",
        "manual_intervention_required_text": "Intervenção Manual Necessária para atualizar o ticket",
        "manual_feedback_submitted": "Comentários Manuais Enviados",
        "full_execution_log": "📜 Registro Completo de Execução:",
        "progress_text": "Progresso: {percent}%",
        "choose_language": "Escolher Idioma",
        "english": "Inglês",
        "spanish": "Espanhol",
        "portuguese": "Português",
        "incident_number": "Número do Incidente: ",
        "incident_description": "Descrição do Incidente: ",
        "agent": "Agente",
        "inc_description": "Problema de autenticação do utilizador Ismart, impossibilidade de utilizar DHAC, IRR. Vários aplicativos afetados.",
        "assignment_desription": "A atribuição foi determinada com base numa combinação de eficiência histórica de resolução, distribuição atual da carga de trabalho e escala de suporte ativa. O Sr. O Suvomoy Nandy foi identificado como o recurso mais adequado para lidar com este incidente, garantindo o tempo mínimo de resolução e a utilização ideal dos recursos.",
        "analysis_summary_info": "O componente afetado é uma dependência de origem para duas aplicações de nível Gold, ambas com suporte para cargas de trabalho transacionais em tempo real.",
        "analysis_disclaimer": "🚨 De acordo com a lógica de priorização do AMS, qualquer falha que impacte um número superior ou igual a duas aplicações Gold, garante uma classificação de Prioridade 2.",
        "analysis_warning": "📈 Portanto, este incidente foi sinalizado para resolução acelerada, a fim de evitar violações de SLA e interrupções para os utilizadores posteriores.",
        "connect_linux": "🔍 Ligar ao servidor Linux...",
        "authenticate_server": "🔐 Autenticando com ID de servidor e password...",
        "fetch_logs": "📁 Obtenção dos registos do caminho do sistema: `/var/logs/app/ARE_application_logs.log`",
        "file_found": "📄 Ficheiro de registo encontrado. A ler agora...\n",
        "no_error": "Nenhum erro encontrado nos registos da aplicação, nenhuma resolução específica recomendada com base nos registos.",
        "self_heal": "🛠️   Iniciar a autocura para:",
        "spinner_self_heal": "A executar Autocura... Por favor aguarde.",
        "oracle_connect": "🔌 Ligar à base de dados Oracle como SYSDBA...",
        "preparing_resolution": "📥 Preparação de consultas de resolução...",
        "executing1": "🧾 Executando: `ALTERAR UTILIZADOR ISMART DESBLOQUEIO DE CUENTA;`",
        "executing2": "🧾 A executar: `ALTERAR UTILIZADOR ISMART IDENTIFICADO POR ismart123;`",
        "self_healing_simulation": "Simulação de auto-cura concluída para: ",
        "executing_sop": "📄 Executar consultas recomendadas pelo SOP...",
        "self_healing_sop": "Simulação de auto-cura concluída com base no SOP.",
        "updated_service_now": "📣 Vou atualizar o ticket no ServiceNow...",
        "updated_success": "Ticket atualizado com sucesso no ServiceNow.",
        "failed_to_close": "❌ Falha ao fechar o ticket:",
        "health_check_spinner": "A executar verificação de integridade... Aguarde.",
        "connection_string": "📄 Tentar ligação usando string de ligação:",
        "connection_successful": "✅ Ligado com sucesso à base de dados em 2,5 segundos.",
        "select_query": "🔍 Verificação de integridade: execução da consulta SELECT para verificar o estado da conta...",
        "query1_executed": "✅ Consulta executada com sucesso em 1,5 segundos.",
        "select_count": "🔍 Verificação de integridade: execução da consulta SELECT COUNT para verificar o estado da conta...",
        "query2_executed": "✅ Consulta executada com sucesso em 1,2 segundos.",
        "completed": "🎉 ✅ Verificação de saúde concluída com sucesso!",
        "generating_problem": "🔍 Gerando Registo de Problema referente à Análise de Causa Raiz...",
        "generating_record": "📝 Gerando descrição do registo...",
        "connect_serviceNow": "🔗 Ligar ao ServiceNow...",
        "register_problem": "📋 Registando registo de problema no ServiceNow...",
        "created_record": "Registo de problema criado no ServiceNow! Número:",
        "failed_record": "Falha ao criar registo. Estado:",
        "details": "Detalhes:",
        "incident_priority": "A definição da prioridade de incidentes é feita no ServiceNow com prioridade : ",
        "incident_assigned": "A atribuição de incidentes é feita para",
        "serviceNow": "em ServiceNow",
        "incident_failed": "Falha no pedido de atualização de incidente:",
        "failed_update": "Falha ao atualizar o tíquete",
        "proceed": "Por favor, escolha como prosseguir.",
        "failed_priority": "Falha ao atualizar a prioridade do tíquete",
        "log_fetch_splunk": "A buscar registos do Splunk",
        "fetching": "Em execução: Pesquisa e validação de dados de incidentes...",
        "impact": "Em execução: Fazendo análise de impacto e atualização da prioridade de incidentes...",
        "assigning": "Em execução: Atribuindo o ticket validado...",
        "extraction": "Execução: Recomendação de extração e resolução de log...",
        "choose": "Selecione abaixo como pretende prosseguir..."
    }
}

# --- Language Selection in UI ---
lang_option = st.sidebar.selectbox(
    translations["en"]["choose_language"],
    options=[translations["en"]["english"], translations["es"]["spanish"], translations["pt"]["portuguese"]],
    index=0
)

# Map language option to language code
lang_code = "en" if lang_option == translations["en"]["english"] else "es" if lang_option == translations["es"]["spanish"] else "pt"


st.markdown("""
<style>
/* Target st.button using class injection */
div.stButton > button {
   background-color: #007BFF;
   color: white;
   padding: 0.7em 1.5em;
   font-size: 16px;
   font-weight: bold;
   border: none;
   border-radius: 8px;
   transition: 0.3s;
   box-shadow: 0 4px 6px rgba(0, 123, 255, 0.3);
}
div.stButton > button:hover {
   background-color: #0056b3;
   color: #fff;
   transform: scale(1.03);
   box-shadow: 0 6px 8px rgba(0, 123, 255, 0.4);
}
</style>
""", unsafe_allow_html=True)

def language_changer(lang_code, text):
    client = APIClient()
    auth = Auth(client)  
    auth.login('2897524', 'Bikram@2897524')
    llm = TCSLLMs(client=client, model_name="gpt-4o")
    if (lang_code == 'en'):
        return text
    else:
        if (lang_code == 'pt'):
            prompt = (
            f"You are a language translator who translates text to portuguese."
            f"Please translate and return the following text to portuguese:\n\n{text}"
            )
        else:
            if (lang_code == 'es'):
                prompt = (
                f"You are a language translator who translates text to spanish."
                f"Please translate and return translate the following text to spanish:\n\n{text}"
                )
    llm_language = llm.invoke(prompt)
    print("LLM language translate")
    print(llm_language)
    return llm_language

def fetch_incident_fields():
    headers = {
        "Accept": "application/json",
    }
    try:
        # Make the GET request to the API
        url = "https://tataconsultancyservicesdemo5.service-now.com/api/now/table/incident?sysparm_query=state%3D5%5Eassignment_group%3D48f128423bc8661011d8057aa5e45a39&sysparm_display_value=true"
        username = "are.integration"
        password = "WF.m(_eOs.-rTQQpd}9LT}jy_QB9ioIifMVJ9b+p$d=-I)%OP>^^FfPsaEf1$I<d?&)CyC81=xfFqZJPuiZi(!z#(D7:9gj&2q3<"

        response = requests.get(
            url,
            headers=headers,
            auth=(username, password)   # Basic authentication
        )
        
        # Print the response code (for debugging or logging purposes)
        print(f"Response code: {response.status_code}")
        
        # Raise an exception if the response contains an HTTP error status code
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return []   # Return an empty list on failure
    
    try:
        # Parse JSON directly from the response
        data = response.json()
        
        # Extract the 'result' field, which contains the tickets
        tickets = data.get("result", [])
        
        # Prepare a list to hold ticket details
        ticket_entities = []
        
        # Loop through the tickets and extract information
        for ticket in tickets:
            # Extract fields with fallback to empty string
            ticket_info = {
                "ticket_number": ticket.get("number", ""),
                "state": ticket.get("state", ""),
                "assigned_to": ticket.get("assigned_to", ""),
                "opened_at": ticket.get("opened_at", ""),
                "short_desc": ticket.get("short_description", ""),
                "description": ticket.get("description", ""),
                "caller": ticket.get("caller_id", {}).get("display_value", ""),
                "assignment_group": ticket.get("assignment_group", {}).get("display_value", ""),
                "priority": ticket.get("priority", ""),
                "config_item": ticket.get("cmdb_ci", {}).get("display_value", ""),
                "sys_id": ticket.get("sys_id", "")
            }
            
            # Append the ticket info to the list
            ticket_entities.append(ticket_info)
        
        # Return the list of ticket entities
        return ticket_entities
    except ValueError as e:
        print(f"Error parsing response JSON: {e}")
        return []


def check_fields_with_llm(description):
    # Define the required fields
    required_fields = [
        "Application Name:- ",
        "Issue Description:- ",
        "No of customer impacted:- ",
        "Date/Timestamp of the issue:- "
    ]
    
    # Create the prompt for the LLM
    prompt = f"""
    You are a validation assistant. Analyze the following incident description and determine if all the required fields
    contain proper and meaningful information. If any field is missing or incomplete, mark it appropriately.
    Here is the incident description:
    
    {description}
    
    The required fields are:
    1. Application Name:-
    2. Issue Description:-
    3. No of customer impacted:-
    4. Date/Timestamp of the issue:-
    
    Respond with a JSON object in the format (without any markdown or code block):
    {{
        "Application Name": "Valid/Incomplete/Missing",
        "Issue Description": "Valid/Incomplete/Missing",
        "No of customer impacted": "Valid/Incomplete/Missing",
        "Date/Timestamp of the issue": "Valid/Incomplete/Missing"
    }}
    """

    try:
        
        client = APIClient()
        auth = Auth(client)  
        auth.login('2897524', 'Bikram@2897524') 
        embeddings = TCSEmbeddings(client, "bge")
        chat = TCSChatModel(client=client, model_name="gpt-4o")
    
        llm_response = chat.invoke(prompt).content
        # Print the LLM Response for debugging (can be removed)
        # print("LLM Response:", llm_response)
    
        # Convert response JSON string to Python dictionary
        validation_results = eval(llm_response)  # Use safer alternatives like `json.loads` for real-world scenarios
    
        # Check if all fields are valid
        return all(value == "Valid" for value in validation_results.values())
    except Exception as e:
        # Handle errors related to OpenAI API
        print(f"Error interacting with OpenAI API: {e}")
        return False
    

def check_fields_in_description(description):
    # Define the required fields
    required_fields = [
        "Application Name:-",
        "Issue Description:-",
        "No of customer impacted:-",
        "Date/Timestamp of the issue:-"
    ]
    
    # Check if all fields are present in the description
    return all(field in description for field in required_fields)

def UpdateAndAssignTicket(sys_id):
    
    insideURL= "https://tataconsultancyservicesdemo5.service-now.com/api/now/table/incident/" + sys_id
    username = "are.integration"
    password = "WF.m(_eOs.-rTQQpd}9LT}jy_QB9ioIifMVJ9b+p$d=-I)%OP>^^FfPsaEf1$I<d?&)CyC81=xfFqZJPuiZi(!z#(D7:9gj&2q3<"

    user_email = "suvomoy.nandy@tcs.com"  # Replace with the actual email
    payload = {
        "assigned_to": user_email,
        "state": "2",
        "work_notes": "Assigned by Auto Assignment Bot"
    }
    
        
    try:
        response = requests.patch(
            insideURL,
            auth=(username, password),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
                },
            verify=False,
            json=payload
            )
        
        if response.status_code not in (200, 204):
            # Do not raise an error here, return a status string
            updateFail = f"{translations[lang_code]['failed_update']}(Status: {response.status_code})."
            return updateFail
        print(f"Update successful. Status code: {response.status_code}")
        returnSuccess = f"{translations[lang_code]['incident_assigned']} {user_email} {translations[lang_code]['serviceNow']}"
        return returnSuccess   # Return success message
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        returnFail = f"{translations[lang_code]['incident_failed']} {e}"
        return returnFail # Return error message

# --- LangGraph State Definition ---
class IncidentProcessingState(TypedDict):
    incidents: List[Dict] # Stores the list of fetched incidents (we'll process the first one)
    current_incident_index: int # Index of the incident being processed
    processing_status: bool # True if incident is valid and pipeline should continue, False otherwise
    stop_reason: str # Reason for stopping if processing_status is False
    assignment_result_message: str # Message from the UpdateAndAssignTicket function
    priority_update_message: str # New field for storing priority update message
    resolution_recommendation: str # New field for storing resolution recommendation - RE-ADDED
    self_healing_result: str # New field for self-healing result
    decision_status: str
    decision_made:bool

# --- Streamlit UI Placeholders and Logging ---
if "logs" not in st.session_state:
    st.session_state.logs = []
if "progress_bar_placeholder" not in st.session_state:
    st.session_state.progress_bar_placeholder = None
if "progress_text_placeholder" not in st.session_state:
   st.session_state.progress_text_placeholder = None
if "status_messages_placeholder" not in st.session_state:
    st.session_state.status_messages_placeholder = None
if "agent_outputs_placeholder" not in st.session_state:
    st.session_state.agent_outputs_placeholder = {} 
if "df_system" not in st.session_state:
    st.session_state.df_system = None   # Will be updated on file upload for Agent 4
if "agent_status_containers" not in st.session_state:
       st.session_state.agent_status_containers = None

if "manual_intervention" not in st.session_state:
    st.session_state.manual_intervention = False
if "ai_result" not in st.session_state:
    st.session_state.ai_result = ""
if "decision_made" not in st.session_state:
    st.session_state["decision_made"] = False
    st.session_state["decision_status"] = None
    st.session_state["confirm_clicked"] = False

# New session state for final state after graph run
if "final_graph_state" not in st.session_state:
    st.session_state["final_graph_state"] = None

def log(message: str):
    st.session_state.logs.append(message)

def update_progress(current_step: int, total_steps: int, message: str):
    # Initialize placeholders if not already set
    if "progress_text_placeholder" not in st.session_state:
        st.session_state.progress_text_placeholder = st.empty()
    if "progress_bar_placeholder" not in st.session_state:
        st.session_state.progress_bar_placeholder = st.empty()
    if "agent_status_containers" not in st.session_state:
        st.session_state.agent_status_containers = [st.container() for _ in range(5)]

    # Calculate progress percentage
    progress_percent = current_step / total_steps

    # Update progress text with larger font and color
    st.session_state.progress_text_placeholder.markdown(
        f"<div style='font-size:24px; font-weight:bold; color:blue; margin-bottom:30px'>{translations[lang_code]['progress_text'].format(percent=int(progress_percent * 100))}</div>",
        unsafe_allow_html=True
    )

    # Update progress bar
    st.session_state.progress_bar_placeholder.progress(progress_percent)
    print(message)
    # Style the message based on its content
    if "Completed" in message: 
        styled_message = f"<div style='font-size:18px; font-weight:bold; color:green;'>{message}</div>"
        line_gap = "<div style='margin-bottom:20px;'></div>"  # Add spacing
    else:
        styled_message = f"<div style='font-size:16px;'>{message}</div>"
        line_gap = ""

    # Append message to the agent-specific container
    agent_index = current_step - 1  # 0-based index
    if 0 <= agent_index < len(st.session_state.agent_status_containers):
        with st.session_state.agent_status_containers[agent_index]:
            st.markdown(styled_message + line_gap, unsafe_allow_html=True)

    # Add a short delay for better visualization
    time.sleep(0.1)



def update_progress2(current_step: int, total_steps: int, message: str):
    if st.session_state.progress_text_placeholder is None:
        st.session_state.progress_text_placeholder = st.empty()
    if st.session_state.progress_bar_placeholder is None:
        st.session_state.progress_bar_placeholder = st.empty()
    if st.session_state.status_messages_placeholder is None:
        st.session_state.status_messages_placeholder = st.empty()
    if st.session_state.agent_status_containers is None:
        st.session_state.agent_status_containers = [st.container() for _ in range(5)]

    progress_percent = current_step / total_steps

    # Update progress text with larger font and color
    st.session_state.progress_text_placeholder.markdown(
        f"<div style='font-size:24px; font-weight:bold; color:blue; margin-bottom:30px'>{translations[lang_code]['progress_text'].format(percent=int(progress_percent * 100))}</div>",
        unsafe_allow_html=True
    )

    # Update progress bar
    st.session_state.progress_bar_placeholder.progress(progress_percent)

    # Determine if the message contains "Completed" and style it accordingly
    # print(message)
    if "Completed" in message:
        # Highlight "Completed" messages with bold, italic, and a different color
        styled_message = f"<div style='font-size:18px; font-weight:bold; color:green;'>{message}</div>"
    else:
        # Default styling for other messages
        #styled_message = f"<div style='font-size:16px; font-style:italic; color:black;'>{message}</div>"
        styled_message = message 

    # Append message to the agent-specific container
    agent_index = current_step - 1  # 0-based index
    if 0 <= agent_index < len(st.session_state.agent_status_containers):
        with st.session_state.agent_status_containers[agent_index]:
            st.markdown(styled_message, unsafe_allow_html=True)
            if "Completed" in message:
                st.write("\n")

    time.sleep(0.1)  # Small sleep to allow UI to update

def update_progress1(current_step: int, total_steps: int, message: str):
    if st.session_state.progress_text_placeholder is None:
        st.session_state.progress_text_placeholder = st.empty()
    if st.session_state.progress_bar_placeholder is None:
        st.session_state.progress_bar_placeholder = st.empty()
    if st.session_state.status_messages_placeholder is None:
        st.session_state.status_messages_placeholder = st.empty()
    if st.session_state.agent_status_containers is None:
       st.session_state.agent_status_containers = [st.container() for _ in range(5)]

    progress_percent = current_step / total_steps
    # st.session_state.progress_bar_placeholder.progress(progress_percent, text=f"Progress: {int(progress_percent * 100)}%")
    st.session_state.progress_text_placeholder.markdown(
       f"<div style='font-size:24px; font-weight:bold;margin-bottom:30px'>{translations[lang_code]['progress_text'].format(percent=int(progress_percent * 100))}</div>",
       unsafe_allow_html=True
    )
    # Update progress bar
    st.session_state.progress_bar_placeholder.progress(progress_percent)
    # st.session_state.status_messages_placeholder.info(message) # Changed to st.info for better visibility
    # 🔥 NEW: Append message to the agent-specific container
    agent_index = current_step - 1  # 0-based index
    if 0 <= agent_index < len(st.session_state.agent_status_containers):
        with st.session_state.agent_status_containers[agent_index]:
            st.markdown(message)
    time.sleep(0.1) # Small sleep to allow UI to update

# --- LangGraph Agents ---

def agent_fetch_and_validate_incident(state: IncidentProcessingState) -> IncidentProcessingState:
    update_progress(1, 5, f"🕵️‍♂️ [{translations[lang_code]['agent']} 1/5] {translations[lang_code]['agent1_title']} {translations[lang_code]['fetching']}") # Adjusted total steps
    log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 1] Fetching incidents from source...")
    
    incidents = fetch_incident_fields() # CALL TO ORIGINAL FUNCTION
    print("List of incidents")
    print(incidents)

    i1 = [{'ticket_number': 'INC0020833', 'state': 'Assigned', 'assigned_to': '', 'opened_at': '2025-07-03 06:36:46', 'short_desc': 'API response times spiked to 2.5s (above SLO of 500ms) during peak traffic hours, causing user timeouts.', 'description': 'Application Name:- DAHC\r\nIssue Description:- NA\r\nNo of customer impacted:- NA\r\nDate/Timestamp of the issue:- NA', 'caller': 'Sudhanshu Singh', 
'assignment_group': 'ARE_TEAM', 'priority': '3 - Medium', 'config_item': 'DHAC', 'sys_id': '8658a90947ee2250e0d0961f016d43f1'}]

    i2 = [{'ticket_number': 'INC0020832', 'state': 'Assigned', 'assigned_to': '', 'opened_at': '2025-07-03 06:25:48', 'short_desc': 'API response times spiked to 2.5s (above SLO of 500ms) during peak traffic hours, causing user timeouts.', 'description': 'API response times spiked to 2.5s (above SLO of 500ms) during peak traffic hours, causing user timeouts.', 'caller': 
'Sudhanshu Singh', 'assignment_group': 'ARE_TEAM', 'priority': '3 - Medium', 'config_item': 'DHAC', 'sys_id': '11d5e90147ee2250e0d0961f016d43ab'}]

    i3 = [{'ticket_number': 'INC0020833', 'state': 'Assigned', 'assigned_to': '', 'opened_at': '2025-07-03 06:36:46', 'short_desc': 'Facing slow internet speed in system', 'description': 'Application Name:- DAHC\r\nIssue Description:- NA\r\nNo of customer impacted:- NA\r\nDate/Timestamp of the issue:- NA', 'caller': 'Sudhanshu Singh', 
'assignment_group': 'ARE_TEAM', 'priority': '3 - Medium', 'config_item': 'DHAC', 'sys_id': '8658a90947ee2250e0d0961f016d43f1'}]

    i4 = [{'ticket_number': 'INC0020844', 'state': 'Assigned', 'assigned_to': '', 'opened_at': '2025-07-08 01:53:24', 'short_desc': translations[lang_code]['inc_description'], 'description': 'Application Name:- DHAC\r\nIssue Description:- Ismart user authentication issue, not able to use DHAC , IRR. Multiple application impacted\r\nNo of customer impacted:- 5\r\nDate/Timestamp of the issue:- 2025-07-01 10:30:00', 'caller': 'Sudhanshu Singh', 'assignment_group': 'ARE_TEAM', 'priority': '3 - Medium', 'config_item': 'DHAC', 'sys_id': 'f767d2ee4726e290e0d0961f016d43e2'}]
    
    i5 = [{'ticket_number': 'INC0020900', 'state': 'Assigned', 'assigned_to': '', 'opened_at': '2025-07-31 06:13:32', 'short_desc': translations[lang_code]['inc_description'], 'description': 'Application Name:- DHAC\r\nIssue Description:- Ismart user authentication issue, not able to use DHAC , IRR. Multiple application impacted\r\nNo of customer impacted :-5\r\nDate/Timestamp of the issue:- 2025-07-01 10:30:00', 'caller': 'Sudhanshu Singh', 'assignment_group': 'ARE_TEAM', 'priority': '3 - Medium', 'config_item': 'DHAC', 'sys_id': 'fe8f25c63b0f221011d8057aa5e45a42'}]
    
    #incidents =i5 # Using a hardcoded incident for demonstration

    if not incidents:
        state["processing_status"] = False
        state["stop_reason"] = translations[lang_code]["no_incidents_found"]
        log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 1] No incidents to process. Stopping.")
        update_progress(5, 5, f"❌ [{translations[lang_code]['agent']} 1/5] {translations[lang_code]['agent1_title']} Completed: {translations[lang_code]['no_incidents_found']}") # Adjusted total steps
        # Dynamic UI output for Agent 1 (failure case)
        if "Agent1" not in st.session_state.agent_outputs_placeholder:
            st.session_state.agent_outputs_placeholder["Agent1"] = st.empty()
        with st.session_state.agent_outputs_placeholder["Agent1"].container():
            st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 🕵️‍♂️ {translations[lang_code]['agent1_title']}</p>", unsafe_allow_html=True)
            st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
            st.error(f"{translations[lang_code]['error_message']} {state['stop_reason']}")
            st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
        return state
    
    # Process the first incident found
    incident = incidents[0]
    state["incidents"] = [incident] # Store the single incident for subsequent agents
    state["current_incident_index"] = 0 # Set index
    
    # Define display_incident here, after state["incidents"] and state["current_incident_index"] are set
    display_incident = state["incidents"][state["current_incident_index"]]

    log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 1] Fetched incident: {incident.get('ticket_number')}")
    
    # Conditional check from original business logic
    #if check_fields_in_description(incident.get('description', '')): # CALL TO ORIGINAL FUNCTION
    if check_fields_with_llm(incident.get('description', '')):      
        state["processing_status"] = True
        log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 1] Incident description fields are complete.")
        update_progress(1, 5, f"✅ [{translations[lang_code]['agent']} 1/5] {translations[lang_code]['agent1_title']} Completed: Incident {incident.get('ticket_number')} fetched and {translations[lang_code]['desc_ok']}") # Adjusted total steps
    else:
        state["processing_status"] = False
        state["stop_reason"] = f"Incident {incident.get('ticket_number')}: {translations[lang_code]['error_message']} Missing required fields in description. Data needs to be rectified."
        log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 1] Incident description fields incomplete. Stopping.")
        update_progress(5, 5, f"⚠️ [{translations[lang_code]['agent']} 1/5] {translations[lang_code]['agent1_title']} Completed: Incident {incident.get('ticket_number')} {translations[lang_code]['desc_incomplete']}") # Adjusted total steps

    # st.markdown("<hr style='border:1px solid seashell; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
    # st.markdown("<p style='text-align:center;font-weight:bold;font-size:26px;color:seashell'>Evaluation and Results of the Agents</p>", unsafe_allow_html=True)
    # st.markdown("<hr style='border:1px solid seashell; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)

    st.markdown("<div style='margin-top : 40px'></div>", unsafe_allow_html=True)
    #st.image("Picture1.png", use_container_width=False)

    # Dynamic UI output for Agent 1
    if "Agent1" not in st.session_state.agent_outputs_placeholder:
        st.session_state.agent_outputs_placeholder["Agent1"] = st.empty()
    with st.session_state.agent_outputs_placeholder["Agent1"].container():
        # st.subheader("🕵️‍♂️ Agent 1 Output: Incident Details & Validation")
        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 🕵️‍♂️ {translations[lang_code]['agent1_title']}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
 
        # col1, col2 = st.columns(2)
        # with col1:
        #     st.metric(label="**Incident Number**", value=display_incident.get('ticket_number'))
        # with col2:
        #     st.metric(label="**Short Description**", value=display_incident.get('short_desc'))
        st.markdown(f"<b>{translations[lang_code]["incident_number"]}</b> {display_incident.get('ticket_number')}",unsafe_allow_html=True)
        st.markdown(f"<b>{translations[lang_code]["incident_description"]}</b> {display_incident.get('short_desc')}",unsafe_allow_html=True)
        with st.expander(translations[lang_code]["view_full_desc"]):
            st.code(display_incident.get('description'))
        
        if state["processing_status"]:
            st.success(translations[lang_code]["data_quality_passed"])
        else:
            st.error(f"{translations[lang_code]['data_quality_failed']} {state['stop_reason']}")
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
    
    return state

def agent_assign_ticket(state: IncidentProcessingState) -> IncidentProcessingState:
    update_progress(3, 5, f"👨‍💻 [{translations[lang_code]['agent']} 3/5] {translations[lang_code]['agent2_title']} {translations[lang_code]['assigning']}") # Adjusted total steps
    log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 3] Attempting to assign ticket...")
    
    # Ensure there's an incident to work with
    if not state.get("incidents") or state.get("current_incident_index", -1) == -1:
        state["assignment_result_message"] = translations[lang_code]["error_no_incident"]
        log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 3] Error: No incident to assign found in state.")
        update_progress(3, 5, f"❌ [{translations[lang_code]['agent']} 3/5] {translations[lang_code]['agent2_title']} Completed: Error, no incident to assign.") # Adjusted total steps
        return state

    current_incident = state["incidents"][state["current_incident_index"]]
    sys_id = current_incident.get("sys_id")
    ticket_number = current_incident.get("ticket_number", "N/A")
    
    if not sys_id:
        state["assignment_result_message"] = f"{translations[lang_code]['error_no_sysid']} {ticket_number} to assign."
        log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 3] Error: No sys_id for ticket {ticket_number}.")
        update_progress(3, 5, f"❌ [{translations[lang_code]['agent']} 3/5] {translations[lang_code]['agent2_title']} Completed: {translations[lang_code]['error_no_sysid']} {ticket_number}.") # Adjusted total steps
        return state

    assignment_message = UpdateAndAssignTicket(sys_id) # CALL TO ORIGINAL FUNCTION
    state["assignment_result_message"] = assignment_message
    log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 3] Ticket Assignment Result: {assignment_message}")
    update_progress(3, 5, f"✅ [{translations[lang_code]['agent']} 3/5] {translations[lang_code]['agent2_title']} Completed: {translations[lang_code]['assignment_finished']} {ticket_number}.") # Adjusted total steps

    # Dynamic UI output for Agent 2
    if "Agent2" not in st.session_state.agent_outputs_placeholder:
        st.session_state.agent_outputs_placeholder["Agent2"] = st.empty()
    with st.session_state.agent_outputs_placeholder["Agent2"].container():
        
        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 👨‍💻 {translations[lang_code]['agent2_title']}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
        if "ServiceNow" in assignment_message: # Check for success message from your UpdateAndAssignTicket
            st.success(f"✅ {assignment_message}")
            st.write(translations[lang_code]['assignment_desription'])
        else:
            st.error(f"❌ {assignment_message}")
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)

    return state

# --- Agent 3: Application Dependency Dashboard (Priority Update) ---
def fetchIaddDataGoldCount(config_item):
    # This is a mock function based on your provided sample_json
    # In a real scenario, this would involve API calls or database lookups
    sample_json = [{'application': 'DHAC', 'region': 'SEAL', 'sector': 'BFSI', 'dependencyDashboard': [{'lob': 'Agentic AMS', 'application': [], 'goldCount': 2, 'gold': [{'application': 'Batch Analyzer', 'Status': 'R'}, {'application': 'ICERT', 'Status': 'A'}], 'silverCount': 1, 'silver': [{'application': 'Triage Bot', 'Status': 'A'}], 'bronze': [{'application': 'IRR', 'Status': 'R'}], 'affectedPortfolioData': [{'portfolioName': 'Agentic AMS', 'tier_1_app': [{'application': 'Batch Analyzer', 'contact': {'name': 'Sudhanshu Singh', 'mail': 'singh.sudhanshu@tcs.com', 'phone': '+1-555-111-2222'}, 'Status': 'R'}, {'application': 'ICERT', 'contact': {'name': 'Sudhanshu Singh', 'mail': 'singh.sudhanshu@tcs.com', 'phone': '+1-555-111-2222'}, 'Status': 'A'}], 'tier_2_app': [{'application': 'Triage Bot', 'contact': {'name': 'Mike Johnson', 'mail': 'mike.johnson@tcs.com', 'phone': '+1-555-555-6666'}, 'Status': 'A'}, {'application': 'IRR', 'Status': 'R', 'contact': {'name': 'Emily Davis', 'mail': 'emily.davis@tcs.com', 'phone': '+1-555-777-8888'}}], 'overallStatus': 'R'}]}]}]
    
    for app in sample_json:
        if config_item == app.get("application"): # Use config_item dynamically
            for dependencyDashboard in app.get("dependencyDashboard"):
                if dependencyDashboard.get("goldCount") >= 2:
                    return 2 # Returns priority 2
    return None # Return None if condition not met or application not found

def UpdatePriorityTicket(sys_id):
    insideURL= "https://tataconsultancyservicesdemo5.service-now.com/api/now/table/incident/" + sys_id
    username = "are.integration"
    password = "WF.m(_eOs.-rTQQpd}9LT}jy_QB9ioIifMVJ9b+p$d=-I)%OP>^^FfPsaEf1$I<d?&)CyC81=xfFqZJPuiZi(!z#(D7:9gj&2q3<"

    payload = {
        "work_notes": "Priority updated by Application Dependency Dashboard",
        "impact" : "2",
        "urgency" : "2"
    }
        
    try:
        response = requests.patch(
            insideURL,
            auth=(username, password),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
                },
            verify=False,
            json=payload
            )
        
        if response.status_code not in (200, 204):
            failed_update_priority = f"{translations[lang_code]['failed_priority']} (Status: {response.status_code})."
            return failed_update_priority
        print(f"Update successful. Status code: {response.status_code}")
        return f"{translations[lang_code]['incident_priority']} {payload['impact']}" # Return success message
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return f"Incident Priority Set failed: {e}" # Return error message

def agent_application_dependency_dashboard(state: IncidentProcessingState) -> IncidentProcessingState:
    # Agent 3 Running message
    # st.session_state.agent_placeholders[2].markdown("🟡 **Agent 3/5: Running - Doing impact analysis and updating priority...**")

    update_progress(2, 5, f"📈 [{translations[lang_code]['agent']} 2/5] {translations[lang_code]['priority_update_title']} {translations[lang_code]['impact']}") # Adjusted total steps
    log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 2] Checking impact analysis and updating incident priority.")

    if not state.get("incidents") or state.get("current_incident_index", -1) == -1:
        state["priority_update_message"] = f"Error: No incident available in state for priority update."
        log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 2] Error: No incident to process for priority update.")
        update_progress(2, 5, f"❌ [{translations[lang_code]['agent']} 2/5] {translations[lang_code]['priority_update_title']} Completed: Error, no incident for priority update.") # Adjusted total steps
        # st.session_state.agent_placeholders[2].error("❌ Agent 2/5: Failed - No incident found for priority update.")
        return state

    current_incident = state["incidents"][state["current_incident_index"]]
    config_item = current_incident.get('config_item', '')
    sys_id = current_incident.get('sys_id', '')
    ticket_number = current_incident.get('ticket_number', 'N/A')

    print(f"Config Item : {config_item}")

    if not config_item or not sys_id:
        state["priority_update_message"] = f"Error: Missing config_item or sys_id for incident {ticket_number} to update priority."
        log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 2] Error: Missing data for priority update on {ticket_number}.")
        update_progress(2, 5, f"❌ [{translations[lang_code]['agent']} 2/5] {translations[lang_code]['priority_update_title']} Completed: Missing data for {ticket_number}.") # Adjusted total steps
        # st.session_state.agent_placeholders[2].error(f"❌ [Agent 2/5] Completed: Missing data for {ticket_number}.")
        return state

    priority_to_set = fetchIaddDataGoldCount(config_item)
    print(f"Priority set to : {priority_to_set}")
    if priority_to_set is not None and priority_to_set >= 2:
        res = UpdatePriorityTicket(sys_id)
        state["priority_update_message"] = res
        log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 2] Priority Update Result for {ticket_number}: {res}")
        update_progress(3, 5, f"✅ [{translations[lang_code]['agent']} 2/5] {translations[lang_code]['priority_update_title']} Completed: {translations[lang_code]['priority_updated']} {ticket_number}.") # Adjusted total steps
        # st.session_state.agent_placeholders[2].success(f"✅ [Agent 2/5] Completed: Priority update for {ticket_number}.")
    else:
        state["priority_update_message"] = f"{translations[lang_code]['priority_not_updated']} {ticket_number}. Gold count condition not met or config item not found."
        log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 2] Priority not updated for {ticket_number}. Condition not met.")
        update_progress(3, 5, f"ℹ️ [{translations[lang_code]['agent']} 2/5] {translations[lang_code]['priority_update_title']} Completed: {translations[lang_code]['priority_not_updated']} {ticket_number}.") # Adjusted total steps
        # st.session_state.agent_placeholders[2].success(f"ℹ️ [Agent 2/5] Completed: Priority not updated for {ticket_number}.")
    # Dynamic UI output for Agent 3
    if "Agent3" not in st.session_state.agent_outputs_placeholder:
        st.session_state.agent_outputs_placeholder["Agent3"] = st.empty()
    with st.session_state.agent_outputs_placeholder["Agent3"].container():
        # st.subheader("📈 Agent 3 Output: Application Impact Analysis & Priority Update")
        
        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 📈 {translations[lang_code]['priority_update_title']}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
        if "ServiceNow" in state["priority_update_message"] or "not met" in state["priority_update_message"].lower():
            st.markdown(f"<p style='text-align: left;'><strong>{translations[lang_code]['iadd_summary']}</strong></p>", unsafe_allow_html=True)
            st.info(translations[lang_code]['analysis_summary_info'])
            st.write(translations[lang_code]['analysis_disclaimer'])
            st.write(translations[lang_code]['analysis_warning'])
            st.info(f"✅ {state['priority_update_message']}")
        else:
            st.error(f"❌ {state['priority_update_message']}")
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)

    return state

# --- Agent 4: Log Extractor and Resolution Recommender ---
# ✅ Hardcoded log and SOP paths (adjust as needed for deployment)
# For this example, ensure 'ARE_application_logs.log' and 'application_SOP.yaml' are in the same directory as this script.
LOG_FILE_PATH = "ARE_application_logs.log"
SOP_FILE_PATH = "application_SOP.yaml"

def extract_error_summary(log_path):
    error_counts = defaultdict(list)
    error_pattern = re.compile(r'ERROR\s+(.*)', re.IGNORECASE)
    # Adjust base_path if log and SOP files are not in the same directory as the script
    # For Streamlit, __file__ might be different, consider using a direct path or st.file_uploader
    # For this example, assuming files are in the same directory.
    # base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")) 
    # log_path = os.path.join(base_path, log_path) # Original
    
    # For this example, assuming log_path is relative to where the script is run
    if not os.path.exists(log_path):
        st.error(f"Error: Log file not found at {log_path}. Please create it or adjust the path.")
        return {}

    with open(log_path, 'r') as f:
        for line in f:
            match = error_pattern.search(line)
            if match:
                error_message = match.group(1).strip()
                key = get_error_key(error_message)
                error_counts[key].append(error_message)
    return error_counts

def read_log_file(path):
   try:
       with open(path, "r") as f:
           return f.readlines()
   except FileNotFoundError:
       return ["❌ Log file not found."]

def get_error_key(error_msg):
    match = re.search(r'(ORA-\d{5})', error_msg)
    if match:
        return match.group(1)
    if "connection" in error_msg.lower():
        return "DB-CONNECTION-ERROR"
    if "login" in error_msg.lower():
        return "ARE-LOGIN-FAILURE"
    return error_msg[:50] # Fallback for other errors

def format_summary(error_dict):
    summary = []
    for key, messages in error_dict.items():
        summary.append(f"- **{key}** occurred {len(messages)} time(s). Example: `{messages[0]}`") # Added backticks for code
    return "\n".join(summary)

def load_sop(file_path):
    try:
        # Adjust base_path if SOP file is not in the same directory as the script
        # base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")) # Original
        # file_path = os.path.join(base_path, file_path) # Original

        # For this example, assuming file_path is relative to where the script is run
        if not os.path.exists(file_path):
            st.error(f"Error: SOP file not found at {file_path}. Please create it or adjust the path.")
            return {}

        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.warning(f"⚠️ Could not load SOP file: {e}") # Changed to st.warning
        return {}

def agent_log_extractor_and_resolution_recommender(state: IncidentProcessingState) -> IncidentProcessingState:
    # st.session_state.agent_placeholders[2].markdown("🟡 [Agent 4/5] Running: Log Extraction and Resolution Recommendation...")
    update_progress(4, 5, f"🔎 [{translations[lang_code]['agent']} 4/5] {translations[lang_code]['log_analysis_title']} {translations[lang_code]['extraction']}")
    log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 4] Starting log analysis and resolution recommendation.")

    llm_output_placeholder = st.session_state.agent_outputs_placeholder.get("Agent4_LLM_Output", st.empty())
    if "Agent4" not in st.session_state.agent_outputs_placeholder:
        st.session_state.agent_outputs_placeholder["Agent4"] = st.empty()
    
    with st.session_state.agent_outputs_placeholder["Agent4"].container():
        
        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 🔎 {translations[lang_code]['log_analysis_title']}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
        
        st.write(translations[lang_code]['connect_linux'])
        time.sleep(1.2)

        st.write(translations[lang_code]['authenticate_server'])
        time.sleep(1)

        st.write(translations[lang_code]['fetch_logs']) # Added backticks
        time.sleep(1.2)

        st.write(translations[lang_code]['file_found'])
        time.sleep(1)

        splunk_base_url = "https://10.169.51.2:8081/api/splunk"
        username = "admin"
        password = "ismart123"
        search_query = r'''search index="main" sourcetype="ARE_DEMO" earliest=@y latest=now | eval raw_cleaned=replace(_raw, "^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ", "") | eval logline = strftime(_time,"%Y-%m-%d %H:%M:%S") . " " . raw_cleaned | table logline'''
        # Create the full URL to the export endpoint
        url = f"{splunk_base_url}/services/search/jobs/export"
        # Form data
        payload = {
            "search": search_query,
            "output_mode": "json"
        }
        output_file = "ARE_application_error.log"

        # Make the request
        # Call Splunk and save output
        with requests.post(url, data=payload, auth=HTTPBasicAuth(username, password), verify=False, stream=True) as response:
            if response.status_code == 200:
                st.write(translations[lang_code]['log_fetch_splunk']) # Added backticks
                with open(output_file, "w", encoding="utf-8") as f:
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line.decode("utf-8"))
                            log_line = data.get("result", {}).get("logline")
                            if log_line:
                                #st.write("📄 Log file found. Reading now...\n")
                                f.write(log_line + "\n")
                print(f"✅ Logs saved to: {output_file}")
            else:
                print(f"❌ Failed to fetch logs: {response.status_code} - {response.text}")


        client = APIClient()
        auth = Auth(client)  
        auth.login('2897524', 'Bikram@2897524')
        llm = TCSLLMs(client=client, model_name="gpt-4o")
        
        #logs = read_log_file(LOG_FILE_PATH)
        logs = read_log_file(output_file)
        if not logs:
            st.warning("No logs found.")
            return
        # Show initial preview (first 10 lines)
        preview_lines = 10
        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:20px;color: aquamarine;'> {translations[lang_code]['log_preview']}</p>", unsafe_allow_html=True)
        st.code("".join(logs[:preview_lines]), language="log")
        # Expandable section for full logs
        with st.expander(translations[lang_code]["view_full_log"]):
            st.code("".join(logs), language="log")
        sop_data = load_sop(SOP_FILE_PATH)
        error_summary_dict = extract_error_summary(LOG_FILE_PATH)
        
        resolution_recommendations_list = [] # To collect recommendations

        if not error_summary_dict:
            st.info(translations[lang_code]["no_logs_found"]) # Changed to st.info
            state["resolution_recommendation"] = translations[lang_code]['no_error']
            log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 4] No errors found in logs.")
        else:
            # st.subheader("") # Changed to subheader
            st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:20px;color: aquamarine;'> {translations[lang_code]['error_summary']}</p>", unsafe_allow_html=True)
            st.code(format_summary(error_summary_dict)) # Use markdown for formatted text

            st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:20px;color: aquamarine;'> {translations[lang_code]['checking_sop']}</p>", unsafe_allow_html=True)

            for key, messages in error_summary_dict.items():
                
                sop_entry = sop_data.get(key)
                if sop_entry:
                    # st.write(f"---") # Separator for each error type
                    st.write(f"{translations[lang_code]['error_type']} `{key}`") # Bold and backticks
                    st.code(f"{translations[lang_code]['sop_found']} {sop_entry.get('title')}") # Changed to st.success
                    st.write(f"{translations[lang_code]['resolution_steps']}") # Bold
                    st.code(sop_entry.get('resolution')) # Use st.code for resolution steps
                        
                    sop_title = sop_entry.get('title')
                    sop_resolution = sop_entry.get('resolution')
                    ai_prompt = (
                        f"You are a senior SRE and DevOps engineer. The following error occurred in application logs: {key} ({sop_title})\n\n"
                        f"SOP Resolution steps were:\n{sop_resolution}\n\n"
                        f"As an expert DevOps/DBA, please provide:\n"
                        f"1. A Root Cause Analysis (RCA)\n"
                        f"2. Long-term or strategic resolution steps to prevent recurrence (mention the steps from SOP also)"
                    )
                    try:
                        # Capture LLM response for state
                        response = llm.invoke(ai_prompt)
                        
                        ai_result = response # Assuming .content gives the string
                        ai_result_translated = language_changer(lang_code,ai_result)
                        # st.subheader("") # Changed to subheader
                        st.session_state.ai_result = ai_result
                        st.divider()
                        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:25px;'> {translations[lang_code]['strategic_recommendation']}</p>", unsafe_allow_html=True)
                        # st.markdown(ai_result) # Use markdown for LLM response
                        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;'>{ai_result_translated}</p>", unsafe_allow_html=True)
                        resolution_recommendations_list.append(f"Error: {key}\nSOP: {sop_title}\nLLM Recommendation:\n{ai_result_translated}\n---")
                    except Exception as e:
                        st.error(f"❌ LLM call failed for {key}: {e}") # Changed to st.error
                        resolution_recommendations_list.append(f"Error: {key}\nLLM Recommendation: Failed to generate ({e})\n---")
                # else:
                #     st.warning(f"---") # Separator
                #     st.warning(f"⚠️ No SOP found for error type: `{key}`") # Changed to st.warning
                #     resolution_recommendations_list.append(f"Error: {key}\nNo SOP found.\n---")
            
            state["resolution_recommendation"] = "\n".join(resolution_recommendations_list)
            #-------automated
            # state["decision_status"] = "human"
            # st.session_state["decision_status"] = "human"
            # state["decision_status"] = "selfheal" # This line will be removed
            # st.session_state["decision_status"] = "selfheal" # This line will be removed
            #--
            log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 4] Generated resolution recommendations.")

    st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
    update_progress(4, 5, f"✅ [{translations[lang_code]['agent']} 4/5] {translations[lang_code]['log_analysis_title']} Completed: Log analysis and resolution recommendations generated.")
    update_progress(4, 5, f"🕵️‍♂️ [{translations[lang_code]['agent']} 5/5] {translations[lang_code]['self_healing_title']} / {translations[lang_code]['agent6_title']}: {translations[lang_code]['choose']}")

        
    return state

# --- Self-Healing Agent ---
def CloseIncident(sys_id):
    insideURL= "https://tataconsultancyservicesdemo5.service-now.com/api/now/table/incident/" + sys_id
    username = "are.integration"
    password = "WF.m(_eOs.-rTQQpd}9LT}jy_QB9ioIifMVJ9b+p$d=-I)%OP>^^FfPsaEf1$I<d?&)CyC81=xfFqZJPuiZi(!z#(D7:9gj&2q3<"

    payload = {
        "close_code": "Solved (Work Around)",
        "close_notes": "Solved(Work Around)",
        "state": "6",
        "work_notes": "Closed by Auto Assignment Bot"
    }
    
    try:
        response = requests.patch(
            insideURL,
            auth=(username, password),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
                },
            verify=False,
            json=payload
            )
        
        if response.status_code not in (200, 204):
            return f"Failed to resolve ticket (Status: {response.status_code})."
        ticket_update = translations[lang_code]['updated_success']
        return ticket_update
    except requests.exceptions.RequestException as e:
        return f"Incident close request failed: {e}" # Return error message

def agent_self_healing(state: IncidentProcessingState) -> IncidentProcessingState:
    update_progress(5, 5, f"🩹 [{translations[lang_code]['agent']} 5/5] {translations[lang_code]['self_healing_title']} Running: Initiating self-healing process...")
    log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 5] Starting self-healing.")

    if "Agent5" not in st.session_state.agent_outputs_placeholder:
        st.session_state.agent_outputs_placeholder["Agent5"] = st.empty()
    
    with st.session_state.agent_outputs_placeholder["Agent5"].container():
        
        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 🩹 {translations[lang_code]['self_healing_title']}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
        
        
        current_incident = state["incidents"][state["current_incident_index"]]
        sys_id = current_incident.get("sys_id", "")
        ticket_number = current_incident.get("ticket_number", "N/A")

        if not sys_id:
            state["self_healing_result"] = f"Error: No sys_id found for incident {ticket_number} to perform self-healing."
            st.error(state["self_healing_result"])
            log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 5] Error: No sys_id for self-healing on {ticket_number}.")
            update_progress(5, 5, f"❌ [{translations[lang_code]['agent']} 5/5] {translations[lang_code]['self_healing_title']} Completed: Error, no sys_id for self-healing on {ticket_number}.")
            st.divider()
            return state

        with st.spinner(translations[lang_code]['spinner_self_heal']):
            error_key = "ORA-28000" # This should ideally come from agent 4's analysis
            st.write(f"{translations[lang_code]['self_heal']} **`{error_key}`**") # Bold and backticks
            time.sleep(1)

            st.write(translations[lang_code]['oracle_connect'])
            time.sleep(1.5)

            st.write(translations[lang_code]['preparing_resolution'])
            time.sleep(1.5)

            if error_key == "ORA-28000":
                st.write(translations[lang_code]['executing1']) # Backticks
                time.sleep(1)
                st.write(translations[lang_code]['executing2']) # Backticks
                time.sleep(1)
                healing_message = f"{translations[lang_code]['self_healing_simulation']}`{error_key}`"
            else:
                st.write(translations[lang_code]['executing_sop'])
                time.sleep(1)
                healing_message = translations[lang_code]['self_healing_sop']

            st.success(f"✅ {healing_message}")
            
            
            st.write(translations[lang_code]['updated_service_now']) # Changed text
            close_result = CloseIncident(sys_id)
            
            if "ServiceNow" in close_result:
                st.success(f"✅ {close_result}")
                state["self_healing_result"] = f"{healing_message}. {close_result}"
            else:
                st.error(f"{translations[lang_code]['failed_to_close']} {close_result}")
                state["self_healing_result"] = f"{healing_message}. Failed to update ticket: {close_result}"
            
        #----Healing

        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 🩹 {translations[lang_code]['health_check_title']}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)

        with st.spinner(translations[lang_code]['health_check_spinner']):
            time.sleep(5)
            st.write(translations[lang_code]['oracle_connect'])
            st.write(f"{translations[lang_code]['connection_string']} jdbc:oracle:thin:@12.33.90.87:1521:XE")
            time.sleep(4)
            st.write(translations[lang_code]['connection_successful'])
            
            st.write(translations[lang_code]['select_query'])
            st.code("📄 SELECT username, account_status FROM dba_users WHERE username = 'ISMART'")
            time.sleep(1.5)
            st.write("📊 Response: Query returned - Username: 'ISMART', Account_Status: 'OPEN'")
            st.write(translations[lang_code]['query1_executed'])
            # st.write("✅ Query executed successfully in 1.5 seconds.")

            st.write(translations[lang_code]['select_count'])
            st.code("📄 SELECT COUNT(*) FROM dba_users WHERE username = 'ISMART' AND account_status = 'OPEN'")
            time.sleep(1.5)
            st.write("📊 Response: Query returned - Count: 1 (indicating the account is unlocked and active)")
            st.write(translations[lang_code]['query2_executed'])

            st.markdown(f"<h4 style='text-align: center; color: green;'>{translations[lang_code]['completed']}</h4>", unsafe_allow_html=True)


    log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 5] Self-healing result: {state['self_healing_result']}")
    st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
    update_progress(5, 5, f"✅ [{translations[lang_code]['agent']} 5/5] {translations[lang_code]['self_healing_title']} Completed: Self-healing process finished.")

    return state



def problem_record_generator():
    
    SERVICENOW_INSTANCE = "https://tataconsultancyservicesdemo5.service-now.com"
    username = "Shankhanil.Ghosh"
    password = "Duke@001"
 
    st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 🩹 {translations[lang_code]['problem_record_title']}</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
    prompt = (
        f"{st.session_state.ai_result}\n\n"
        f"From the following content above, based on the Root Cause Analysis (RCA):\n\n"
        f"Please provide:\n"
        f"1. A Problem Record (1-liner)\n"
        f"2. A Problem Description for registering a problem record in ServiceNow."
        f"Please respond in the following JSON format and dont append any other text, respond only and only the json:\n"
    f'{{\n  "Problem Record": "your one-liner here",\n  "Problem Description": "your detailed description here"\n}}\n\n'

    )
    
    # Step 2: Call LLM
    client = APIClient()
    auth = Auth(client)  
    auth.login('2897524', 'Bikram@2897524')
    llm = TCSLLMs(client=client, model_name="gpt-4o")
    llm_response = llm.invoke(prompt)
    
    
    print("LLM Response")
    print(llm_response)
    # Step 3: Parse LLM response
    #llm_response = eval(llm_response)
    
    
    match = re.search(r'\{.*\}', llm_response, re.DOTALL)
    json_str = match.group()
    llm_response = json.loads(json_str)

    st.info(translations[lang_code]['generating_problem'])
    time.sleep(2)
    problem_record = llm_response.get("Problem Record", "Default Short Description")
    translated_text = language_changer(lang_code, problem_record)
    st.write(translated_text)

    st.info(translations[lang_code]['generating_record'])
    time.sleep(2)
    problem_description = llm_response.get("Problem Description", "Default Long Description")
    translated_text = language_changer(lang_code, problem_description)
    st.write(translated_text)

    # problem_record = "Default Short Description"
    # problem_description = "Default Long Description"
    st.info(translations[lang_code]['connect_serviceNow'])
    time.sleep(2)
    
    payload = {
        "category": "Database",
        "subcategory": "Oracle",
        "short_description": problem_record,
        "cmdb_ci": "IRR",
        "description": problem_description,
        "assignment_group" : "ARE_TEAM"

    }
    st.info(translations[lang_code]['register_problem'])
    url = f"{SERVICENOW_INSTANCE}/api/now/table/problem"
    response = requests.post(
        url,
        auth=HTTPBasicAuth(username, password),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        verify=False,
        json=payload
    )

    if response.status_code == 201:
        result = response.json()
        st.success(f"{translations[lang_code]['created_record']} {result['result']['number']}")
    else:
        st.error(f"{translations[lang_code]['failed_record']} {response.status_code}\n{translations[lang_code]['details']} {response.text}")
    return

def agent_human_healing(state: IncidentProcessingState) -> IncidentProcessingState:
    #update_progress(5, 5, "🩹 [Agent 5/5] Manual Intervention Running: Initiating Human Intervention process...")
    log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 5] Starting Human Intervention")
    #time.sleep(5)
    print("Entered human healing")
    if "Agent6" not in st.session_state.agent_outputs_placeholder:
        st.session_state.agent_outputs_placeholder["Agent6"] = st.empty()
    # a = st.empty()
    # with a.container():
    with st.session_state.agent_outputs_placeholder["Agent6"].container():
        
        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 🩹 {translations[lang_code]['agent6_title']}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
        st.info(translations[lang_code]["manual_intervention_required"])
        

        st.session_state.manual_intervention = True
        
        
    log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 5] Manual Intervention processed {state['self_healing_result']}")
    st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
    update_progress(5, 5, f"✅ [{translations[lang_code]['agent']} 5/5] {translations[lang_code]['agent6_title']} Required")
    return state

# --- Conditional Edge Function ---
def should_assign_or_recommend_cond(state: IncidentProcessingState) -> str:
    """
    Determines if the ticket assignment should proceed or if resolution recommendation
    should be generated, based on processing_status.
    Returns "assign" to proceed to AgentAssignTicket, "recommend_resolution" to AgentResolutionRecommender,
    or "end" to stop the graph.
    """
    if state.get("processing_status", False): # Default to False if not set
        log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Conditional check: Description valid. Proceeding to Agent 2 (Assign Ticket).")
        return "assign"
    else:
        log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Conditional check: Description invalid. Stopping pipeline. Reason: {state.get('stop_reason', 'Condition not met.')}")
        return "end"


# --- Conditional Edge Function ---
# REMOVED THIS FUNCTION: should_selfheal_or_human_cond
# This logic will now be handled by Streamlit UI and direct function calls.
def persistolddata():
    state = st.session_state.final_graph_state
    display_incident = state["incidents"][state["current_incident_index"]]
    #st.write(f"**Incident Number:** {display_incident.get('ticket_number')}")


def persistolddata1():
    state = st.session_state.final_graph_state

    
    # for msg in st.session_state.progressbar_message:
    #     st.markdown(f"{msg}")


    # --- RE-DRAW AGENT 1 OUTPUT ---
    st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 🕵️‍♂️ {translations[lang_code]['agent1_title']}</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
    if not state.get("incidents"):
            st.error(f"{translations[lang_code]['error_message']} {state.get('stop_reason', 'No incidents found.')}")
    else:
        display_incident = state["incidents"][0]
        print(state["incidents"])
        st.markdown(f"<b>{translations[lang_code]["incident_number"]}</b> {display_incident.get('ticket_number')}",unsafe_allow_html=True)
        st.markdown(f"<b>{translations[lang_code]["incident_description"]}</b> {display_incident.get('short_desc')}",unsafe_allow_html=True)
        with st.expander(translations[lang_code]["view_full_desc"]):
            st.code(display_incident.get('description'))
        if state["processing_status"]:
            st.success(translations[lang_code]["data_quality_passed"])
        else:
            st.error(f"{translations[lang_code]['data_quality_failed']} {state.get('stop_reason')}")
    st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)


    # --- RE-DRAW AGENT 2-4 OUTPUT (if they ran) ---
    if state.get("processing_status"):
        # Re-draw Agent 3 Output
        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 📈 {translations[lang_code]['priority_update_title']}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
        priority_message = state.get("priority_update_message", "")
        if "ServiceNow" in priority_message or "not met" in priority_message.lower():
            st.markdown(f"<p style='text-align: left;'><strong>{translations[lang_code]['iadd_summary']}</strong></p>", unsafe_allow_html=True)
            st.info(translations[lang_code]['analysis_summary_info'])
            st.write(translations[lang_code]['analysis_disclaimer'])
            st.write(translations[lang_code]['analysis_warning'])
            st.info(f"✅ {priority_message}")
        else:
            st.error(f"❌ {priority_message}")
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)

        
        # Re-draw Agent 2 Output
        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 👨‍💻 {translations[lang_code]['agent2_title']}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
        assignment_message = state.get("assignment_result_message", "")
        if "ServiceNow" in assignment_message:
            st.success(f"✅ {assignment_message}")
            st.write(translations[lang_code]['assignment_desription'])
        else:
            st.error(f"❌ {assignment_message}")
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)

        #----moved the 3 before 2
        # Re-draw Agent 4 Output
        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 🔎 {translations[lang_code]['log_analysis_title']}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
        #st.markdown("*(Simulating log retrieval and analysis...)*")

        #Adding leftover logextractordetails--->
        st.write(translations[lang_code]['connect_linux'])
        st.write(translations[lang_code]['authenticate_server'])
        st.write(translations[lang_code]['fetch_logs']) # Added backticks
        st.write(translations[lang_code]['file_found'])
        logs = read_log_file(LOG_FILE_PATH)
        if not logs:
            st.warning("No logs found.")
        # Show initial preview (first 10 lines)
        preview_lines = 10
        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:20px;color: aquamarine;'> {translations[lang_code]['log_preview']}</p>", unsafe_allow_html=True)
        st.code("".join(logs[:preview_lines]), language="log")
        # Expandable section for full logs
        with st.expander(translations[lang_code]["view_full_log"]):
            st.code("".join(logs), language="log")
        sop_data = load_sop(SOP_FILE_PATH)
        error_summary_dict = extract_error_summary(LOG_FILE_PATH)
        
        resolution_recommendations_list = [] # To collect recommendations

        if not error_summary_dict:
            st.info(translations[lang_code]["no_logs_found"]) # Changed to st.info
            state["resolution_recommendation"] = translations[lang_code]['no_error']
            log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 4] No errors found in logs.")
        else:
            # st.subheader("") # Changed to subheader
            st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:20px;color: aquamarine;'> {translations[lang_code]['error_summary']}</p>", unsafe_allow_html=True)
            st.code(format_summary(error_summary_dict)) # Use markdown for formatted text

            st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:20px;color: aquamarine;'> {translations[lang_code]['checking_sop']}</p>", unsafe_allow_html=True)

            for key, messages in error_summary_dict.items():
                
                sop_entry = sop_data.get(key)
                if sop_entry:
                    # st.write(f"---") # Separator for each error type
                    st.write(f"{translations[lang_code]['error_type']} `{key}`") # Bold and backticks
                    st.code(f"{translations[lang_code]['sop_found']} {sop_entry.get('title')}") # Changed to st.success
                    st.write(f"{translations[lang_code]['resolution_steps']}") # Bold
                    st.code(sop_entry.get('resolution')) 

    #----end of leftoverdtetails



        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:20px;color: aquamarine;'> {translations[lang_code]['strategic_recommendation']}</p>", unsafe_allow_html=True)
        st.markdown(state.get("resolution_recommendation", "No recommendation generated."))
        #st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)

#----end of persist old data


# --- Streamlit UI Main Function ---
def main():
    st.subheader(translations[lang_code]["title"]) # Changed to st.title with emojis
    st.markdown(
        f"<p style='text-align: right;'><strong>{translations[lang_code]['credits']}</strong></p>",
        unsafe_allow_html=True
    )

    st.info(translations[lang_code]["info_text"])


    if st.button(translations[lang_code]["run_pipeline_button"]):
        
        # Clear previous run's UI elements and logs
        st.session_state.logs = []
        st.session_state.agent_outputs_placeholder = {}
        st.session_state.progress_bar_placeholder = None
        st.session_state.progress_text_placeholder = None
        st.session_state.status_messages_placeholder = None
        st.session_state.agent_status_containers = None
        st.session_state["decision_made"] = False # Reset decision status
        st.session_state["decision_status"] = None # Reset decision
        st.session_state["confirm_clicked"] = False
        st.session_state["final_graph_state"] = None # Clear previous graph state

        st.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {translations[lang_code]['run_pipeline']}")

        # Initialize global UI placeholders for progress and status
        st.session_state.progress_bar_placeholder = st.empty()
        st.session_state.progress_text_placeholder = st.empty()
        st.session_state.status_messages_placeholder = st.empty()
        st.session_state.agent_status_containers = [st.container() for _ in range(5)]

        # Build the LangGraph
        builder = StateGraph(IncidentProcessingState)
        builder.add_node("AgentFetchAndValidate", agent_fetch_and_validate_incident)
        builder.add_node("AgentAssignTicket", agent_assign_ticket)
        builder.add_node("AgentApplicationDependencyDashboard", agent_application_dependency_dashboard)
        builder.add_node("AgentLogExtractorAndResolutionRecommender", agent_log_extractor_and_resolution_recommender)
        # AgentSelfHealing and AgentHumanHealing are no longer part of this graph

        builder.set_entry_point("AgentFetchAndValidate")

        # Conditional edge: After AgentFetchAndValidate, decide whether to assign or end
        builder.add_conditional_edges(
            "AgentFetchAndValidate", # Source node
            should_assign_or_recommend_cond, # Function to call for decision
            {
                "assign": "AgentApplicationDependencyDashboard",
                #"assign": "AgentAssignTicket", # If should_assign_or_recommend_cond returns "assign", go to AgentAssignTicket
                "end": END                   # If should_assign_or_recommend_cond returns "end", stop the graph
            }
        )
        # After AgentAssignTicket, proceed to AgentApplicationDependencyDashboard
        builder.add_edge("AgentApplicationDependencyDashboard", "AgentAssignTicket")
        #builder.add_edge("AgentAssignTicket", "AgentApplicationDependencyDashboard")
       
        # After AgentApplicationDependencyDashboard, proceed to AgentLogExtractorAndResolutionRecommender
        builder.add_edge("AgentAssignTicket", "AgentLogExtractorAndResolutionRecommender")
        #builder.add_edge("AgentApplicationDependencyDashboard", "AgentLogExtractorAndResolutionRecommender")
        
        # After AgentLogExtractorAndResolutionRecommender, the pipeline ENDS
        builder.add_edge("AgentLogExtractorAndResolutionRecommender", END) 

        graph = builder.compile()
        
        # Initial state for the graph (populated by agents)
        initial_state = {
            "incidents": [],
            "current_incident_index": -1,
            "processing_status": False,
            "decision_status": "", # This will be set by user input now
            "decision_made" : False,
            "stop_reason": "",
            "assignment_result_message": "",
            "priority_update_message": "",
            "resolution_recommendation": "", # Re-initialized new field
            "self_healing_result": "" # Initialize new field
        }

        # Invoke the graph for the first part of the pipeline
        st.session_state["final_graph_state"] = graph.invoke(initial_state)

    # Check if the first part of the pipeline has run and ended successfully
    if st.session_state["final_graph_state"] and st.session_state["final_graph_state"].get("processing_status", False):
        
        #st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; font-weight:bold;font-size:26px'>{translations[lang_code]['decision_required']}</p>", unsafe_allow_html=True)
        
        
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
        st.markdown(translations[lang_code]['proceed'])
        
        col1, col2 = st.columns(2)
        with col1:
            confirm = st.button(translations[lang_code]["self_healing"])

        # Place a button in the second column
        with col2:
            confirmHuman = st.button(translations[lang_code]["manual_intervention"])
        #confirm = st.button("✅ Confirm Decision", key="confirm_button")
        
        # Step 3: If confirm clicked, update session_state and run the final agent
        
        if confirm:
            persistolddata1()
            st.session_state["confirm_clicked"] = True
            st.session_state["decision_status"] = "selfheal"
            st.session_state["decision_made"] = True
            # Run AgentSelfHealing separately, passing the last state from LangGraph
            st.session_state["final_graph_state"] = agent_self_healing(st.session_state["final_graph_state"])
            problem_record_generator()
        elif confirmHuman:
            #time.sleep(10)
            persistolddata1()
            st.session_state["confirm_clicked"] = True
            print("Entered Humn elif")
            st.session_state["decision_status"] = "human"
            
            # Run AgentHumanHealing separately, passing the last state from LangGraph
            a= agent_human_healing(st.session_state["final_graph_state"])
            st.session_state["final_graph_state"] = a
            
            
    if st.session_state["manual_intervention"]:
        
        persistolddata1()
        st.markdown(f"<p style='text-align:left; font-weight:bold;font-size:24px;color: gold;margin: 40px 0px -20px 0px'> 🩹 {translations[lang_code]['agent6_title']}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid gold; margin-top:20px; margin-bottom:20px;' />", unsafe_allow_html=True)
        
        user_input = st.text_area(
            translations[lang_code]["feedback_prompt"],
            placeholder=translations[lang_code]["feedback_placeholder"],
            height=200  # Set the height of the text area in pixels
        )
        if st.button(translations[lang_code]["submit_button"]):
            if user_input:
                st.success(translations[lang_code]["feedback_submitted"])
                log(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [Agent 5] Manual Feedback Submitted")
                st.session_state["decision_made"] = True
            else:
                st.warning(translations[lang_code]["enter_feedback"])
            # Rerun to update the UI with the result of the final agent
            #st.rerun()

    # Display final pipeline outcome if decision has been made or pipeline stopped early
    if st.session_state["final_graph_state"] and (st.session_state["decision_made"] or not st.session_state["final_graph_state"].get("processing_status", False)):
        st.markdown(f"<div style='font-size:32px; text-align:center;font-weight: bold;'>{translations[lang_code]['pipeline_complete']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:22px; text-align:left;margin-top : 20px'>{translations[lang_code]['final_outcome']}</div>", unsafe_allow_html=True)
        with st.expander(translations[lang_code]["log_expander"]):
            final_state = st.session_state["final_graph_state"]
            if final_state.get("processing_status", False) or st.session_state["decision_made"]:
                if final_state.get('incidents') and final_state.get('current_incident_index') != -1:
                    ticket_num = final_state['incidents'][final_state['current_incident_index']].get('ticket_number', 'N/A')
                    st.success(f"{translations[lang_code]['successfully_processed'].replace('**', ticket_num)}") # Added emoji
                    st.subheader(f"{translations[lang_code]['final_assignment_status']}") # Changed to subheader
                    st.info(final_state.get('assignment_result_message', 'N/A')) # Changed to st.info
                    st.subheader(f"{translations[lang_code]['priority_update_status']}") # Changed to subheader
                    st.info(final_state.get('priority_update_message', 'N/A')) # Changed to st.info
                    st.subheader(f"{translations[lang_code]['recommended_resolution']}") # Changed to subheader
                    st.code(final_state.get('resolution_recommendation', 'N/A')) # Changed to st.code
                    
                    if st.session_state["decision_status"] == "selfheal": 
                        st.subheader(f"{translations[lang_code]['self_healing_closure_status']}") # Changed to subheader
                        st.info(final_state.get('self_healing_result', 'N/A')) # Changed to st.info
                    elif st.session_state["decision_status"] == "human": 
                        st.info(translations[lang_code]["manual_intervention_required_text"])
                        st.info(translations[lang_code]["manual_feedback_submitted"]) # Changed to st.info
                else:
                    st.success(f"Pipeline finished, but no specific incident outcome available (possibly an edge case).")
            else: # Pipeline stopped early
                st.error(f"{translations[lang_code]['pipeline_stopped']}") # Added emoji
                st.write(f"{translations[lang_code]['reason_for_stop']} {final_state.get('stop_reason', 'Unknown reason.')}")
                if final_state.get('incidents') and final_state.get('current_incident_index') != -1:
                    ticket_num = final_state['incidents'][final_state['current_incident_index']].get('ticket_number', 'N/A')
                    st.info(f"{translations[lang_code]['incident_involved']}{ticket_num}**")
                st.warning(translations[lang_code]["no_further_agents"]) # Changed to st.warning
                
        st.markdown("---") # Separator
        # st.subheader("") # Changed to st.header with emoji
        st.markdown(f"<div style='font-size:22px; text-align:left;'>{translations[lang_code]['full_execution_log']}</div>", unsafe_allow_html=True)
        with st.expander(translations[lang_code]["log_expander"]): # Added expander
            for message in st.session_state.logs:
                st.write(language_changer(lang_code,message))
        
if __name__ == "__main__": 
    main()