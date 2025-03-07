# schema.py
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import Movie as MovieModel, db, Genre as GenreModel
from sqlalchemy.orm import Session

class Genre(SQLAlchemyObjectType):
    class Meta:
        model = GenreModel

class Movie(SQLAlchemyObjectType):
    class Meta:
        model = MovieModel

class Query(graphene.ObjectType):
    movies = graphene.List(Movie)
    search_movies = graphene.List(Movie, title=graphene.String(), director=graphene.String(), year=graphene.Int())
    movies_by_genre = graphene.Field(Movie, genre_id=graphene.ID(required=True))
    genre_by_movie = graphene.Field(Genre, movie_id=graphene.ID(required=True))



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
    
    def resolve_movies_by_genre(root, info, genre_id):
        movie = db.session.get(Movie, genre_id)
        return movie
    
    def resolve_genre_by_movie(root, info, movie_id):
        genre = db.session.get(Genre, movie_id)
        return genre
    
class AddMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        director = graphene.String(required=True)
        year = graphene.Int(required=True)
        genre_id = graphene.Int(required=True)

    movie = graphene.Field(Movie)

    def mutate(root, info, title, director, year, genre_id):
        with Session(db.engine) as session: 
            with session.begin():
                movie = MovieModel(title=title, director=director, year=year, genre_id=genre_id)
                session.add(movie)
            
            session.refresh(movie)
            return AddMovie(movie=movie)

class UpdateMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        director = graphene.String()
        year = graphene.Int()
        genre_id = graphene.Int()

    movie = graphene.Field(Movie)

    def mutate(root, info, id, title=None, director=None, year=None, genre_id=None):
        movie = db.session.get(MovieModel, id)         
        if not movie:
            return None
        if title:    
            movie.title = title
        if director:
            movie.director = director
        if year:
            movie.year = year
        if genre_id:
            movie.genre_id = genre_id
        db.session.commit()
        return UpdateMovie(movie=movie)

class DeleteMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    message = graphene.String()

    def mutate(root, info, id):
        movie = db.session.get(MovieModel, id)         
        if not movie:
            return DeleteMovie(message="That movie does not exist")
        else:
            db.session.delete(movie)
            db.session.commit()
            return DeleteMovie(message="Success")

class Mutation(graphene.ObjectType):
    create_movie = AddMovie.Field()
    update_movie = UpdateMovie.Field()
    delete_movie = DeleteMovie.Field()

class AddGenre(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        movie_id = graphene.Int(required=False)

    genre = graphene.Field(Genre)

    def mutate(root, info, name, movie_id):
        with Session(db.engine) as session: 
            with session.begin():
                genre = GenreModel(name=name, movie_id=movie_id)
                session.add(genre)
            
            session.refresh(genre)
            return AddGenre(genre=genre)

class UpdateGenre(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        movie_id = graphene.Integer()

    movie = graphene.Field(Movie)

    def mutate(root, info, id, name=None, movie_id=None):
        genre = db.session.get(MovieModel, id)         
        if not genre:
            return None
        if name:    
            genre.name = name
        if movie_id:    
            genre.movie_id = movie_id
        db.session.commit()
        return UpdateGenre(genre=genre)

class DeleteGenre(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    message = graphene.String()

    def mutate(root, info, id):
        genre = db.session.get(MovieModel, id)         
        if not genre:
            return DeleteGenre(message="That genre does not exist")
        else:
            db.session.delete(genre)
            db.session.commit()
            return DeleteGenre(message="Success")

schema = graphene.Schema(query=Query, mutation=Mutation)