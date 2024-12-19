from fastapi import APIRouter, Depends, HTTPException
from .ai_service import get_answer
from sqlalchemy.orm import Session
from models.user import User
from models.progress import Progress
from datetime import datetime

async def generate_recommendation_message(improvement_percentage, language='en'):
    """
    Generate a recommendation message based on the improvement percentage.

    Args:
        improvement_percentage (int): The percentage of improvement.
        language (str): The language for the message ('en' or 'es').

    Returns:
        str: The recommendation message.
    """
    if language == 'es':
        request_msg_AI = f"He mejorado un {improvement_percentage}% en mi nivel de estrés. ¿Puedes darme algunos mensajes motivacionales y sugerencias o prácticas recomendadas?"
    else:
        request_msg_AI = f"I have improved {improvement_percentage}% in my stress level. Can you tell me some motivational messages and suggestions or recommended practices?"
    
    ai_response = await get_answer(request_msg_AI)
    return ai_response.get('response')

async def generate_notifications(email: str, db: Session): 
    """
    Generate notifications for a user based on their progress.

    Args:
        username (str): The username of the user.
        db (Session): The database session.

    Returns:
        str: The generated notification message.

    Raises:
        HTTPException: If the user is not found.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = user.id
    user_progress = db.query(Progress).filter(Progress.user_id == user_id).all()
    if not user_progress:
        return generate_motivational_message(-100) 

    # Calculate improvement percentage (example logic)
    initial_stress_level = int(user_progress[0].stress_level)
    latest_stress_level = int(user_progress[-1].stress_level)
    improvement_percentage = int(((initial_stress_level - latest_stress_level) / initial_stress_level) * 100)

    # Generate motivational message using AI service
    motivational_message = generate_motivational_message(improvement_percentage)

    # Generate recommendation message using AI service
    recommendation_message = await generate_recommendation_message(improvement_percentage)
    
    result_message = motivational_message + "\n" + recommendation_message

    return result_message

def generate_motivational_message(improvement_percentage: int, language='en'):
    """
    Generate a motivational message based on the improvement percentage.

    Args:
        improvement_percentage (int): The percentage of improvement.
        language (str): The language for the message ('en' or 'es').

    Returns:
        str: The motivational message.
    """
    messages = {
        'en': {
            100: "You did it! 100% progress—congratulations! You’ve achieved your goal through hard work and determination. Celebrate your success—you’ve earned it!",
            95: "You’re so close—95% of the way there! The effort you’ve put in is paying off, and you’re about to achieve something incredible. Keep up the great work!",
            92: "92% progress is something to be proud of! You’re just steps away from success, and the progress you’ve made is truly inspiring. Keep pushing forward!",
            89: "You’re 89% of the way there—amazing work! You’ve shown so much resilience, and you’re almost at your goal. Keep going strong—you’ve got this!",
            86: "You’ve reached 86%, and that’s a huge accomplishment! The finish line is within reach, and your persistence is getting you closer every day.",
            83: "83% progress is incredible! You’ve shown so much dedication, and you’re getting closer to your goal with each step. Stay focused—you’re nearly there!",
            80: "Reaching 80% is something to celebrate! You’re almost at the finish line, and the hard work you’ve put in is paying off. Keep going—you’re almost there!",
            77: "You’re three-quarters of the way there! The progress you’ve made so far is proof of your perseverance. Stay strong, and keep up the amazing work.",
            74: "74% is a huge milestone! You’re making real strides, and every step you take brings you closer to the finish line. You’ve got this—keep going!",
            71: "71% progress means you’re well on your way to achieving your goal. Keep pushing forward, and remember that you’re capable of even greater things.",
            68: "You’re nearly at 70%, and your progress is something to be proud of. Keep your momentum going—you’re doing amazing work for your mental well-being.",
            65: "You’ve come so far! 65% of the way there means you’re closer to your goal than ever. Stay committed—you’re doing something truly great for yourself.",
            62: "62% progress is amazing! You’re getting closer to your goal with every effort you make. Keep going, and remember that you’re building lasting change.",
            59: "You’ve made so much progress! Keep your eyes on the path ahead, and trust that each step you take is leading you toward success.",
            56: "56% of the way, and you’re doing incredible! The dedication you’ve shown is making a real difference. Stay focused, and keep believing in yourself.",
            53: "You’re more than halfway through your journey, and that’s a huge accomplishment! Keep going—the changes you’re making are creating a brighter future.",
            50: "Halfway there! The progress you’ve made so far is proof of your strength. Keep pushing forward, and trust that you’re capable of even more.",
            46: "Almost halfway there! You’ve already proven your strength and resilience, and you’re getting closer to your goals with each passing day.",
            43: "43% and going strong! The effort you’re putting in is leading you toward the peace and balance you deserve. Stay patient with yourself.",
            40: "Reaching 40% is no small feat! You’re moving closer to your goal every day. Keep believing in yourself—you’re stronger than you realize.",
            37: "You’re more than a third of the way through your journey! Your dedication is paying off, and you’re creating lasting, positive change.",
            34: "34% of the way there! You’re showing remarkable commitment, and the progress you’re making is something to be proud of. Don’t stop now!",
            31: "You’re making real progress! Every small effort you make is contributing to a better, healthier version of yourself. Keep up the good work!",
            28: "28% progress means you’re building positive momentum! Stay focused, keep practicing what’s working, and trust that you’re moving toward your goals.",
            25: "You’ve reached 25%, and that’s a big achievement! Keep pushing forward—your resilience is shining through, and you’re doing amazing.",
            22: "Great job! You’re making steady progress, and each step forward is proof of your determination. Keep practicing those healthy habits!",
            19: "Almost at 20%! You’re laying a solid foundation for your mental health journey. Stay focused, and remember you’re stronger than you think.",
            16: "Your hard work is beginning to pay off. You’re making important progress, and the changes you’re striving for are within reach.",
            13: "You’re showing true strength by staying committed. Keep going—the steps you’re taking now are leading you to a brighter future.",
            10: "Reaching 10% is a great start! Celebrate the small victories, and trust that you’re building momentum toward greater progress.",
            7: "You're starting to make headway! Stay patient with yourself—change takes time, and you’re doing exactly what you need to.",
            4: "Progress might feel slow, but every bit adds up. Be proud of your efforts, and remember that each day brings new opportunities for growth.",
            1: "You’ve taken the first step, and that’s the hardest part! Every small effort counts. Keep moving forward—you’re on the right track.",
            -100: "Welcome! 🌟 You've taken a brave step by seeking support, and that’s something to be proud of. Remember, you’re not alone in this journey. We’re here to help you explore what’s weighing you down and find ways to lift that burden, one step at a time. Healing takes time, so be gentle with yourself. You deserve peace, joy, and healing. Let’s begin this journey toward a brighter future together! 💙",
            'default': "Keep going! Every bit of progress counts, and you’re doing great."
        },
        'es': {
            100: "¡Lo lograste! 100% de progreso—¡felicitaciones! Has alcanzado tu objetivo a través del trabajo duro y la determinación. Celebra tu éxito—¡te lo has ganado!",
            95: "¡Estás tan cerca—95% del camino! El esfuerzo que has puesto está dando sus frutos, y estás a punto de lograr algo increíble. ¡Sigue con el gran trabajo!",
            92: "¡El 92% de progreso es algo de lo que estar orgulloso! Estás a solo pasos del éxito, y el progreso que has hecho es verdaderamente inspirador. ¡Sigue adelante!",
            89: "¡Estás al 89% del camino—trabajo increíble! Has mostrado tanta resiliencia, y estás casi en tu objetivo. Sigue fuerte—¡lo tienes!",
            86: "¡Has alcanzado el 86%, y eso es un gran logro! La línea de meta está al alcance, y tu persistencia te está acercando cada día más.",
            83: "¡El 83% de progreso es increíble! Has mostrado tanta dedicación, y te estás acercando a tu objetivo con cada paso. Mantente enfocado—¡casi llegas!",
            80: "¡Alcanzar el 80% es algo para celebrar! Estás casi en la línea de meta, y el trabajo duro que has puesto está dando sus frutos. Sigue adelante—¡casi llegas!",
            77: "¡Estás a tres cuartos del camino! El progreso que has hecho hasta ahora es prueba de tu perseverancia. Mantente fuerte, y sigue con el increíble trabajo.",
            74: "¡El 74% es un gran hito! Estás haciendo verdaderos avances, y cada paso que das te acerca a la línea de meta. ¡Lo tienes—sigue adelante!",
            71: "El 71% de progreso significa que estás bien encaminado para alcanzar tu objetivo. Sigue adelante, y recuerda que eres capaz de cosas aún mayores.",
            68: "¡Estás casi al 70%, y tu progreso es algo de lo que estar orgulloso! Mantén tu impulso—estás haciendo un trabajo increíble para tu bienestar mental.",
            65: "¡Has llegado tan lejos! El 65% del camino significa que estás más cerca de tu objetivo que nunca. Mantente comprometido—estás haciendo algo verdaderamente grandioso para ti mismo.",
            62: "¡El 62% de progreso es increíble! Estás acercándote a tu objetivo con cada esfuerzo que haces. Sigue adelante, y recuerda que estás construyendo un cambio duradero.",
            59: "¡Has hecho tanto progreso! Mantén tus ojos en el camino por delante, y confía en que cada paso que das te está llevando hacia el éxito.",
            56: "¡El 56% del camino, y estás haciendo un trabajo increíble! La dedicación que has mostrado está haciendo una verdadera diferencia. Mantente enfocado, y sigue creyendo en ti mismo.",
            53: "¡Estás más de la mitad de tu viaje, y eso es un gran logro! Sigue adelante—los cambios que estás haciendo están creando un futuro más brillante.",
            50: "¡A mitad de camino! El progreso que has hecho hasta ahora es prueba de tu fuerza. Sigue adelante, y confía en que eres capaz de aún más.",
            46: "¡Casi a mitad de camino! Ya has demostrado tu fuerza y resiliencia, y te estás acercando a tus objetivos con cada día que pasa.",
            43: "¡El 43% y sigue fuerte! El esfuerzo que estás poniendo te está llevando hacia la paz y el equilibrio que mereces. Sé paciente contigo mismo.",
            40: "¡Alcanzar el 40% no es poca cosa! Estás acercándote a tu objetivo cada día. Sigue creyendo en ti mismo—eres más fuerte de lo que crees.",
            37: "¡Estás más de un tercio del camino en tu viaje! Tu dedicación está dando sus frutos, y estás creando un cambio positivo y duradero.",
            34: "¡El 34% del camino! Estás mostrando un compromiso notable, y el progreso que estás haciendo es algo de lo que estar orgulloso. ¡No te detengas ahora!",
            31: "¡Estás haciendo un progreso real! Cada pequeño esfuerzo que haces está contribuyendo a una mejor y más saludable versión de ti mismo. ¡Sigue con el buen trabajo!",
            28: "¡El 28% de progreso significa que estás construyendo un impulso positivo! Mantente enfocado, sigue practicando lo que está funcionando, y confía en que te estás moviendo hacia tus objetivos.",
            25: "¡Has alcanzado el 25%, y eso es un gran logro! Sigue adelante—tu resiliencia está brillando, y estás haciendo un trabajo increíble.",
            22: "¡Gran trabajo! Estás haciendo un progreso constante, y cada paso adelante es prueba de tu determinación. ¡Sigue practicando esos hábitos saludables!",
            19: "¡Casi al 20%! Estás sentando una base sólida para tu viaje de salud mental. Mantente enfocado, y recuerda que eres más fuerte de lo que piensas.",
            16: "Tu arduo trabajo está comenzando a dar sus frutos. Estás haciendo un progreso importante, y los cambios que estás buscando están al alcance.",
            13: "Estás mostrando una verdadera fuerza al mantenerte comprometido. Sigue adelante—los pasos que estás dando ahora te están llevando a un futuro más brillante.",
            10: "¡Alcanzar el 10% es un gran comienzo! Celebra las pequeñas victorias, y confía en que estás construyendo un impulso hacia un mayor progreso.",
            7: "¡Estás comenzando a avanzar! Sé paciente contigo mismo—el cambio lleva tiempo, y estás haciendo exactamente lo que necesitas.",
            4: "El progreso puede parecer lento, pero cada poco suma. Esté orgulloso de tus esfuerzos, y recuerda que cada día trae nuevas oportunidades para crecer.",
            1: "¡Has dado el primer paso, y eso es lo más difícil! Cada pequeño esfuerzo cuenta. Sigue adelante—estás en el camino correcto.",
            -100: "¡Bienvenido! 🌟 Has dado un paso valiente al buscar apoyo, y eso es algo de lo que estar orgulloso. Recuerda, no estás solo en este viaje. Estamos aquí para ayudarte a explorar lo que te pesa y encontrar formas de aliviar esa carga, paso a paso. La curación lleva tiempo, así que sé amable contigo mismo. Mereces paz, alegría y sanación. ¡Comencemos este viaje hacia un futuro más brillante juntos! 💙",
            'default': "¡Sigue adelante! Cada pequeño progreso cuenta, y lo estás haciendo genial."
        }
    }

    # Filter out non-integer keys for comparison
    percentage_keys = [k for k in messages[language].keys() if isinstance(k, int)]
    percentage_keys = sorted(percentage_keys, reverse=True)

    # Find the matching message
    for threshold in percentage_keys:
        if improvement_percentage >= threshold:
            return messages[language][threshold]
    
    # Return default message if no matching threshold is found
    return messages[language]['default']
