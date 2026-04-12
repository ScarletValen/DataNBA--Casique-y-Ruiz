#LIMPIEZA DE LA BASE DE DATOS
library(tidyverse)
library(kableExtra)
df_original <- read.csv("30. NBA.csv")
df_original_sin_nulos <- df_original %>%
  drop_na(contains("home"), contains("away"))

#FILTRADO Y MANIPULACIÓN DE DATOS EN LA TEMPORADA 2019

df_2019 <- df_original_sin_nulos %>% filter(SEASON == 2019)
view(df_2019)
cat("\n=== TEMPORADA 2019 ===\n")
cat("Filas:", nrow(df_2019))

#Revision de los valores nulos en la temporada 2019 de la NBA
nulos_en_columnas <- colSums(is.na(df_2019))
nulos_en_columnas <- nulos_en_columnas[nulos_en_columnas > 0]
if(length(nulos_en_columnas) > 0)
  cat("===VALORES NULOS ===\n")
print(nulos_en_columnas)
cat("Total de celdas con nulos:", sum(nulos_en_columnas), "\n")

#Revisión de datos duplicados
datos_duplicados <- sum(duplicated(df_2019))
if(datos_duplicados > 0)
  cat("\n=== Datos Duplicados ===\n")
cat("Filas_duplicadas:", datos_duplicados, "\n")
