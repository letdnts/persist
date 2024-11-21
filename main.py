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

class Voo (BaseModel):
        id_voo: int
        numero_voo: int
        origem: str
        destino:str
        horario_partida: datetime
        horario_chegada: datetime
        id_aeronave: int
        id_piloto: int
        status:str

@app.post("/voos/")
def inserir_voo(voo: Voo):
        file_exists = os.path.isfile(CSV_FILE)

        try:
               with open(CSV_FILE, "a") as file:
                      writer = csv.writer(file)

                      if not file_exists:
                            writer.writerow(["id_voo", "numero_voo", "origem", 
                                             "destino","horario_partida", "horario_chegada",
                                              "id_aeronave", "id_piloto", "status"
                            ])
                        
                      writer.writerow([
                             voo.id_voo, voo.numero_voo,  voo.origem,  
                             voo.destino, voo.horario_partida, voo.horario_chegada, 
                             voo.id_aeronave,  voo.id_piloto,  voo.status
                      ])
        except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro ao salvar dados: {e}")  
        return {"message": "Voo inserido com sucesso!"}

        

