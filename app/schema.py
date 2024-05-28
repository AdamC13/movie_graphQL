# schema.py
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import Movie as MovieModel, db
from sqlalchemy.orm import Session

class Movie(SQLAlchemyObjectType):
    class Meta:
        model = MovieModel

class Query(graphene.ObjectType):
    movies = graphene.List(Movie)
    search_movies = graphene.List(Movie, title=graphene.String(), director=graphene.String(), year=graphene.Int())

    def resolve_movies(root, info):
        return db.session.execute(db.select(MovieModel)).scalars()

    def resolve_search_movies(root, info, title=None, director=None, year=None):        
        query = db.select(MovieModel)
        if title:
            query = query.where(MovieModel.title.ilike(f'%{title}%'))
        if director:
            query = query.where(MovieModel.director.ilike(f'%{director}%'))
        if year:
            query = query.where(MovieModel.year == year)
        results = db.session.execute(query).scalars().all()
        return results
    
class AddMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        director = graphene.String(required=True)
        year = graphene.Int(required=True)

    movie = graphene.Field(Movie)

    def mutate(root, info, title, director, year):
        with Session(db.engine) as session: 
            with session.begin():
                movie = MovieModel(title=title, director=director, year=year)
                session.add(movie)
            
            session.refresh(movie)
            return AddMovie(movie=movie)

class UpdateMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        director = graphene.String()
        year = graphene.Int()

    movie = graphene.Field(Movie)

    def mutate(root, info, id, title=None, director=None, year=None):
        movie = db.session.get(MovieModel, id)         
        if not movie:
            return None
        if title:    
            movie.title = title
        if director:
            movie.director = director
        if year:
            movie.year = year
        db.session.commit()
        return UpdateMovie(movie=movie)

class DeleteMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    message = graphene.String()

    def mutate(root, info, id):
        movie = db.session.get(MovieModel, id)         
        if not movie:
            return "That movie does not exist"
        else:
            db.session.delete(movie)
            db.session.commit()
            return "Success"

class Mutation(graphene.ObjectType):
    create_movie = AddMovie.Field()
    update_movie = UpdateMovie.Field()
    delete_movie = DeleteMovie.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)