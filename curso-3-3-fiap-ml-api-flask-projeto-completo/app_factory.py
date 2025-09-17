# app_factory.py
from flask import Flask, request, jsonify
from config import Config
from extensions import db, jwt, swagger
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)

    # importa modelos e rotas aqui dentro (após init_app)
    from models import User, Recipe  # noqa: F401

    @app.route("/")
    def home():
        """
        Home
        ---
        tags:
          - Health
        summary: Página inicial / healthcheck simples
        responses:
          200:
            description: OK
            schema:
              type: string
              example: Pagina inicial
        """
        return "Pagina inicial"

    @app.route("/register", methods=["POST"])
    def register_user():
        """
        Registrar usuário
        ---
        tags:
          - Auth
        summary: Cria um novo usuário
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [username, password]
              properties:
                username:
                  type: string
                  example: sostenes
                password:
                  type: string
                  example: 123456
        responses:
          201:
            description: Usuário criado com sucesso
            schema:
              type: object
              properties:
                msg:
                  type: string
                  example: User Created
          400:
            description: Usuário já existe
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: User already exists
        """
        data = request.get_json()
        if User.query.filter_by(username=data["username"]).first():
            return jsonify({"error": "User already exists"}, 400)

        new_user = User(username=data["username"], password=data["password"])
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"msg": "User Created"}), 201

    @app.route("/login", methods=["POST"])
    def login():
        """
        Login
        ---
        tags:
          - Auth
        summary: Autentica usuário e retorna um JWT
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [username, password]
              properties:
                username:
                  type: string
                  example: sostenes
                password:
                  type: string
                  example: 123456
        responses:
          200:
            description: Autenticado com sucesso
            schema:
              type: object
              properties:
                access_token:
                  type: string
                  example: eyJ0eXAiOiJKV1QiLCJhbGciOi...
          401:
            description: Credenciais inválidas
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Invalid credentials
        """
        data = request.get_json()
        user = User.query.filter_by(username=data["username"]).first()
        if user and user.password == data["password"]:
            token = create_access_token(identity=str(user.id))
            return jsonify({"access_token": token}), 200

        return jsonify({"error": "Invalid credentials"}), 401

    @app.route("/protected", methods=["GET"])
    @jwt_required()
    def protected():
        """
        Rota protegida
        ---
        tags:
          - Auth
        summary: Exemplo de rota que exige JWT
        security:
          - BearerAuth: []
        responses:
          200:
            description: Acesso autorizado
            schema:
              type: object
              properties:
                msg:
                  type: string
                  example: Usuário com id 1 acessou a rota protegida.
          401:
            description: Token não fornecido ou inválido
        """
        current_user_id = get_jwt_identity()
        return (
            jsonify(
                {"msg": f"Usuário com id {current_user_id} acessou a rota protegida."}
            ),
            200,
        )

    @app.route("/recipes", methods=["POST"])
    @jwt_required()
    def create_recipe():
        """
        Criar receita
        ---
        tags:
          - Recipes
        summary: Cria uma nova receita
        security:
          - BearerAuth: []
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
                type: object
                required: [title, ingredients, time_minutes]
                properties:
                  title:
                    type: string
                    example: Bolo de Cenoura
                  ingredients:
                    type: string
                    example: Farinha, ovos, cenoura, açúcar, óleo
                  time_minutes:
                    type: integer
                    example: 45
        responses:
          201:
            description: Receita criada
            schema:
              type: object
              properties:
                msg:
                  type: string
                  example: Recipe created
          401:
            description: Token não fornecido ou inválido
        """
        data = request.get_json()
        new_recipe = Recipe(
            title=data["title"],
            ingredients=data["ingredients"],
            time_minutes=data["time_minutes"],
        )
        db.session.add(new_recipe)
        db.session.commit()
        return jsonify({"msg": "Recipe created"}), 201

    @app.route("/recipes", methods=["GET"])
    def get_recipes():
        """
        Listar receitas
        ---
        tags:
          - Recipes
        summary: Lista receitas com filtros opcionais
        parameters:
          - in: query
            name: ingredient
            required: false
            type: string
            description: Filtra por ingrediente (busca parcial)
            example: ovos
          - in: query
            name: max_time
            required: false
            type: integer
            description: Tempo máximo de preparo em minutos
            example: 30
        responses:
          200:
            description: Lista de receitas
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  title:
                    type: string
                    example: Bolo de Cenoura
                  ingredients:
                    type: string
                    example: Farinha, ovos, cenoura, açúcar, óleo
                  time_minutes:
                    type: integer
                    example: 45
        """
        ingredient = request.args.get("ingredient")
        max_time = request.args.get("max_time", type=int)

        query = Recipe.query
        if ingredient:
            query = query.filter(Recipe.ingredients.ilike(f"%{ingredient}%"))
        if max_time is not None:
            query = query.filter(Recipe.time_minutes <= max_time)

        recipes = query.all()
        return (
            jsonify(
                [
                    {
                        "id": r.id,
                        "title": r.title,
                        "ingredients": r.ingredients,
                        "time_minutes": r.time_minutes,
                    }
                    for r in recipes
                ]
            ),
            200,
        )

    @app.route("/recipes/<int:recipe_id>", methods=["PATCH"])
    @jwt_required()
    def update_recipe(recipe_id):
        """
        Atualizar receita
        ---
        tags:
          - Recipes
        summary: Atualiza campos de uma receita existente
        security:
          - BearerAuth: []
        parameters:
          - in: path
            name: recipe_id
            required: true
            type: integer
            description: ID da receita
            example: 1
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                title:
                  type: string
                  example: Bolo de Cenoura (cobertura de chocolate)
                ingredients:
                  type: string
                  example: Farinha, ovos, cenoura, açúcar, óleo, chocolate
                time_minutes:
                  type: integer
                  example: 50
        responses:
          200:
            description: Receita atualizada
            schema:
              type: object
              properties:
                msg:
                  type: string
                  example: Recipe updated
          401:
            description: Token não fornecido ou inválido
          404:
            description: Receita não encontrada
        """
        data = request.get_json()
        recipe = Recipe.query.get_or_404(recipe_id)

        if "title" in data:
            recipe.title = data["title"]
        if "ingredients" in data:
            recipe.ingredients = data["ingredients"]
        if "time_minutes" in data:
            recipe.time_minutes = data["time_minutes"]

        db.session.commit()
        return jsonify({"msg": "Recipe updated"}), 200

    @app.route("/recipes/<int:recipe_id>", methods=["DELETE"])
    @jwt_required()
    def delete_recipe(recipe_id):
        """
        Remover receita
        ---
        tags:
          - Recipes
        summary: Remove uma receita pelo ID
        security:
          - BearerAuth: []
        parameters:
          - in: path
            name: recipe_id
            required: true
            type: integer
            description: ID da receita
            example: 1
        responses:
          200:
            description: Receita removida
            schema:
              type: object
              properties:
                msg:
                  type: string
                  example: Recipe deleted
          401:
            description: Token não fornecido ou inválido
          404:
            description: Receita não encontrada
        """
        recipe = Recipe.query.get_or_404(recipe_id)
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({"msg": "Recipe deleted"}), 200

    return app
