from fractions import Fraction

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from gourmetweb.db import get_db

bp = Blueprint('recipe', __name__)


def pretty_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    total_time = []
    if hours > 0:
        total_time.append(f'{hours} hour{"s" if hours > 1 else ""}')
    if minutes > 0:
        total_time.append(f'{minutes} minute{"s" if minutes > 1 else ""}')
    if seconds > 0:
        total_time.append(f'{seconds} second{"s" if seconds > 1 else ""}')

    return ' '.join(total_time)


def pretty_number(value):
    if value is None:
        return ''
        
    whole_number = int(value)
    fractional_number = value % 1
    if fractional_number == 0:
        return str(whole_number)
    else:
        pretty = str(whole_number) if whole_number != 0 else ''
        return  pretty + ' ' + str(Fraction(fractional_number).limit_denominator(8))


def get_pretty_ingredients(db, recipe_id):
    ingredients = db.execute(
        'SELECT position, amount, rangeamount, unit, item, optional, inggroup'
        ' FROM ingredients'
        ' WHERE recipe_id=?',
        (recipe_id, )
    ).fetchall()

    ingredients_sorted = []
    for ingr in ingredients:
        ingr_parts = []
        amount_pretty = pretty_number(ingr['amount'])
        if ingr['rangeamount'] is not None:
            amount_pretty += ' - ' + pretty_number(ingr['rangeamount'])
        if len(amount_pretty) > 0:
            ingr_parts.append(amount_pretty)

        if ingr['unit'] is not None:
            ingr_parts.append(ingr['unit'])
        
        ingr_parts.append(ingr['item'])
        ingredient = ' '.join(ingr_parts)

        ingredients_sorted.append((
            ingr['position'],
            ingr['inggroup'] if ingr['inggroup'] is not None else '',
            {'ingredient': ingredient,
             'optional': ingr['optional'] != 0
            }
        ))
    ingredients_sorted.sort()

    # Get order of ingredient groups
    group_order = []
    for i in ingredients_sorted:
        group = i[1]
        if group not in group_order:
            group_order.append(group)

    group_ingredients_pretty = []
    for group in group_order:
        group_ingredients = []
        for i in ingredients_sorted:
            if i[1] == group:
                group_ingredients.append(i[2])
        group_ingredients_pretty.append((group, group_ingredients))
    
    return group_ingredients_pretty


@bp.route('/')
def index():
    db = get_db()
    recipes = db.execute(
        'SELECT id, title, rating, yields, yield_unit, preptime, cooktime'
        ' FROM recipe R'
    ).fetchall()
    return render_template('recipe/index.html', recipes=recipes)


@bp.route('/<int:id>/')
def recipe(id):
    db = get_db()

    recipe = db.execute(
        'SELECT title, rating, yields, yield_unit, preptime, cooktime,'
        ' instructions, modifications, cuisine, link'
        ' FROM recipe'
        ' WHERE id=?',
        (id, )
    ).fetchone()

    if recipe is None:
        abort(404, "Recipe id {0} doesn't exist.".format(id))

    data = dict(**recipe)

    data['preptime_pretty'] = pretty_time(data['preptime'])
    data['cooktime_pretty'] = pretty_time(data['cooktime'])
    data['instructions_pretty'] = [i for i in data['instructions'].splitlines() if len(i.strip()) > 0]
    data['ingredients_pretty'] = get_pretty_ingredients(db, id)
    
    return render_template('recipe/recipe.html', recipe=data)
