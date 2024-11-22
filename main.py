from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import os
import zipfile
import hashlib
from datetime import datetime


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Serviço de Gerenciamento de Voos"}

CSV_FILE = "voos.csv"

header = ["id_voo", "numero_voo", "cia", "origem", 
          "destino", "horario_partida", "horario_chegada", 
          "id_aeronave", "status"]

class Voo (BaseModel):
        id_voo: int
        numero_voo: int
        cia: str
        origem: str
        destino:str
        horario_partida: datetime
        horario_chegada: datetime
        id_aeronave: int
        status:str

@app.post("/voos/")
def inserir_voo(voo: Voo):
        file_exists = os.path.isfile(CSV_FILE)

        try:
               with open(CSV_FILE, "a") as file:
                      writer = csv.writer(file)

                      if not file_exists:
                            writer.writerow(["id_voo", "numero_voo", "cia" "origem", 
                                             "destino","horario_partida", "horario_chegada",
                                              "id_aeronave", "status"
                            ])
                        
                      writer.writerow([
                             voo.id_voo, voo.numero_voo, voo.cia,  voo.origem,  
                             voo.destino, voo.horario_partida, voo.horario_chegada, 
                             voo.id_aeronave,  voo.status
                      ])
        except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro ao salvar dados: {e}")  
        return {"message": "Voo inserido com sucesso!"}

        
@app.get("/contar_registros")
def contar_registros():
        try:
               file = open(CSV_FILE, mode="r")
               reader = csv.reader(file)
               next(reader)
               count = sum(1 for line in reader)
               return {"Total de Registros": count}
        except FileNotFoundError:
                return {"error": "Arquivo CSV não encontrado."}
        except Exception as e:
                return {"error": f"Erro ao contar registros: {str(e)}"}
                file.close()

