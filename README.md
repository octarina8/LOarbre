# LOArbre — Árbol genealógico familiar

Árbol genealógico interactivo publicado con [Topola Genealogy Viewer](https://github.com/PeWu/topola-viewer).

## Ver el árbol

**Link directo (con fotos):**
https://octarina8.github.io/LOArbre/#/view?gen=0&handleCors=false&indi=I0001&url=https%3A%2F%2Foctarina8.github.io%2FLOArbre%2FLOArbre.gdz

**Link alternativo:**
https://octarina8.github.io/LOArbre/#/view?url=https://octarina8.github.io/LOArbre/LOArbre.gdz&handleCors=false

---

## Cómo funciona (para otros proyectos)

Si quieres montar tu propio árbol, el patrón de la URL es:

```
https://TU_USUARIO.github.io/arbol-familiar/#/view?url=https://TU_USUARIO.github.io/arbol-familiar/mi-arbol.ged&handleCors=false
```

---

## Cómo actualizar el árbol online

1. **Exportar desde Gramps:** Archivo → Exportar → formato GEDCOM → sobreescribir `LOArbre.ged`

2. **Regenerar el `.gdz`** (empaqueta el `.ged` con todas las fotos):
   ```
   python make-gdz.py
   ```

3. **Subir a GitHub:**
   ```
   git add .
   git commit -m "actualización árbol"
   git push
   ```

4. **Esperar unos minutos** y abrir el link para ver los cambios.
