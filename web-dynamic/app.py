from os import environ
from flask import Flask, render_template, url_for, request, redirect, flash

app = Flask(__name__)
app.config["SECRET_KEY"] = 'b5f141eba28c4b881306889ca5c714c6ed937fcb92b15ce40b83e991fb908068'
csv_file_path = "static/Online_registration_info/csv_file/SAM '24 Wedding Registration Form.csv"


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/invitees-form', methods=['GET', 'POST'])
def form():

    if request.method == 'POST':
        from models.invitees import Invitees
        from models.engine import storage

        if request.form.get('info'):
            if not request.form.get('value').strip().isdigit():
                flash('{} is not a digit', 'danger')
                return redirect(url_for('form'))
            data = storage.session().query(Invitees).filter_by(pass_code=request.form.get('passcode').strip()).first()
            if not data:
                flash(f"{request.form.get('passcode')}, does not exist")
                return redirect(url_for('form'))
            if request.form.get('info') == 'table':
                data.table_number = request.form.get('value')
            elif request.form.get('info') == 'chair':
                data.chair_number = request.form.get('value')
            storage.session().commit()
            flash('successful update', 'success')
            return redirect(url_for('form'))

        elif request.form.get('status-info'):
            data = storage.session().query(Invitees).filter_by(pass_code=request.form.get('passcode').strip()).first()
            if not data:
                flash(f"{request.form.get('passcode')}, does not exist")
                return redirect(url_for('form'))
            data.relationship_with_sam24 = request.form.get('status-info')
            data.chair_number = get_chair_number(request.form.get('status-info'))
            storage.session().commit()
            flash('successful update', 'success')
            return redirect(url_for('form'))

        elif request.form.get('table-no'):
            status = request.form.get('table-status-info')
            value = request.form.get('table-no')
            if not value.isdigit():
                flash(f'{value} is not a digit!', 'danger')
                return redirect(url_for('form'))
            for invitee in storage.session().query(Invitees).filter_by(relationship_with_sam24=status).all():
                invitee.table_number = int(request.form.get('table-no'))
            storage.session().commit()
            flash('successful update', 'success')
            return redirect(url_for('form'))

        elif request.form.get('del-passcode'):
            import os

            invitee = storage.session().query(Invitees).filter_by(pass_code=request.form.get('del-passcode').strip()).first()
            if not invitee:
                flash('Invitee not Found', 'danger')
                return redirect(url_for('form'))
            storage.session().delete(invitee)
            storage.session().commit()
            pic_path = f"static/invitees_images/{invitee.profile_pic_file_name}"
            os.remove(pic_path)
            flash('deleted successfully', 'success')
            return redirect(url_for('form'))

        fullname = request.form.get('fullname').strip()
        email = request.form.get('email').strip()
        phone_address = request.form.get('phone_address').strip()

        # check redundant
        all_invitees = storage.session().query(Invitees).all()
        for invitee in all_invitees:
            if fullname == invitee.fullname:
                flash(f"The Name '{invitee.fullname}' already Exist in the database", 'danger')
                return redirect(url_for('form'))
            elif email == invitee.email:
                flash(f"The Gmail Address '{invitee.email}' already Exist in the database", 'danger')
                return redirect(url_for('form'))
            elif phone_address == invitee.phone_address:
                flash(f"The Phone Address '{invitee.phone_address}' already Exist in the database", 'danger')
                return redirect(url_for('form'))

        pass_code = passcode_generator()
        new_invite = Invitees(
            fullname=fullname,
            email=email,
            phone_address=phone_address,
            profile_pic_file_name=save_profile_pic(pass_code=pass_code, picture=request.files['profile-pic']),
            pass_code=pass_code,
            chair_number=get_chair_number(request.form.get('status')),
            relationship_with_sam24=request.form.get('status')
        )
        storage.session().add(new_invite)
        storage.session().commit()
        flash('Update Successful', 'success')
        return redirect(url_for('form'))

    return render_template('form.html')


@app.route('/verification-search/<passcode>', methods=['GET', 'POST'])
def verification_search(passcode='0'):

    if request.method == 'POST':
        return redirect(url_for('verification_search', passcode=request.form.get('search')))

    from models.engine import storage
    from models.invitees import Invitees
    invitee = storage.session().query(Invitees).filter_by(pass_code=passcode).first()
    if not invitee:
        if passcode == 0:
            invitee = 0
        else:
            invitee = passcode
    return render_template('search.html', invitee=invitee)


@app.route('/invitee_statistics')
def invitees_stat():
    from models.engine import storage
    from models.invitees import Invitees

    invitees = storage.session().query(Invitees).order_by('relationship_with_sam24', 'chair_number').all()
    return render_template('registered_invitees.html', invitees=invitees)


@app.route('/unregistered_invitee_statistics')
def unregistered_invitees_stat():
    from models.engine import storage
    from models.invitees import Invitees
    import csv
    with open(csv_file_path, 'r') as f:
        datas = csv.DictReader(f)
        datas = [row for row in datas]
    unregistered_invitees = []
    for data in datas:
        if not storage.session().query(Invitees).filter_by(fullname=data['Full Name'].strip()).first():
            unregistered_invitees.append(data)
    for x in unregistered_invitees:
        print(x)
    return render_template('unregistered_invitees.html', invitees=unregistered_invitees)


@app.route('/registration-automation')
def automate_reg():
    import csv
    from models.invitees import Invitees
    from models.engine import storage
    import os
    from PIL import Image

    profile_pic_dir_path = "static/Online_registration_info/Profile_pic"

    with open(csv_file_path, 'r') as f:
        datas = csv.DictReader(f)
        json_data = [row for row in datas]

    for invitee in json_data:
        if storage.session().query(Invitees).filter_by(email=invitee['Gmail Address']).first():
            continue

        try:
            pass_code = passcode_generator()
            profile_pic_name = None

            if not profile_pic_name:
                import re
                fullname = invitee['Full Name'].lower()
                print('Gmail domain', fullname)
                picture_match = 0
                for pic_name in os.listdir(profile_pic_dir_path):
                    pic_list = re.split(r'[.\-_ ]+', pic_name)
                    print(pic_list)
                    i = 0
                    for pic in pic_list:
                        if pic.lower() in fullname:
                            i += 1

                    if i >= 2:
                        profile_pic_name = pic_name
                        picture_match += 1
                if picture_match > 1:
                    profile_pic_name = None

            if not profile_pic_name:
                import re
                gmail_domain = invitee['Gmail Address'].split('@')[0].replace('.', '').lower()
                print('Gmail domain', gmail_domain)
                picture_match = 0
                for pic_name in os.listdir(profile_pic_dir_path):
                    pic_list = re.split(r'[.\-_ ]+', pic_name)
                    print(pic_list)
                    i = 0
                    for pic in pic_list:
                        if pic.lower() in gmail_domain:
                            i += 1

                    if i >= 2:
                        profile_pic_name = pic_name
                        picture_match += 1
                if picture_match > 1:
                    profile_pic_name = None

            if not profile_pic_name:
                continue

            picture_full_path = os.path.join(profile_pic_dir_path, profile_pic_name).replace('\\', '/')

            picture = Image.open(picture_full_path)

            if invitee["Your Relationship with the Celebrants"] == "Siblings' Invitees":
                status = invitee['Select Your Related Sibling'] + "'s Invitees"
            else:
                status = invitee["Your Relationship with the Celebrants"]

            new_invite = Invitees(
                fullname=invitee['Full Name'].strip(),
                email=invitee['Gmail Address'].strip(),
                phone_address=invitee['Phone Number'].strip(),
                profile_pic_file_name=save_profile_pic(pass_code=pass_code, picture=picture),
                pass_code=pass_code,
                # table_number=False,
                chair_number=get_chair_number(status),
                relationship_with_sam24=status
            )
            storage.session().add(new_invite)
            storage.session().commit()
            os.remove(picture_full_path)
        except:
            continue
    return redirect(url_for('form'))


def save_profile_pic(pass_code, picture):
    import os

    try:
        _, file_ext = os.path.splitext(picture.filename)
    except AttributeError:
        _, file_ext = os.path.splitext(picture.info.get('filename'))

    file_name = f'{pass_code}{file_ext}'.replace("'", "")
    path = f'static/invitees_images/{file_name}'
    picture.save(path)
    return file_name


@app.route('/arrange_all')
def arrange_all():
    from models.engine import storage
    from models.invitees import Invitees

    prev = None
    for invite in storage.session().query(Invitees).order_by('relationship_with_sam24', 'chair_number').all():
        new = invite
        if prev is None:
            new.chair_number = 1
            prev = new
            continue
        if new.relationship_with_sam24 == prev.relationship_with_sam24:
            new.chair_number = prev.chair_number + 1
            prev = new
            continue
        else:
            new.chair_number = 1
            prev = new
            continue
    storage.session().commit()
    return redirect(url_for('form'))


@app.route('/send_passcode')
def send_passcode():
    from models.engine import storage
    from models.invitees import Invitees

    email_subject = "SAM'24 Passcode Notification"

    for invitee in storage.session().query(Invitees).all():
        message = generate_message(invitee.fullname, invitee.pass_code)

        send_message(invitee.email, email_subject, message)

    return redirect(url_for('invitees_stat'))


def passcode_generator():
    import secrets
    from models.engine import storage
    from models.invitees import Invitees

    all_invitees = storage.session().query(Invitees).all()
    passcode = "SAM'24" + secrets.token_hex(2)
    for invitee in all_invitees:
        if passcode == invitee.pass_code:
            passcode = passcode_generator()

    return passcode


def get_chair_number(status):
    from models.invitees import Invitees
    from models.engine import storage

    session = storage.session()
    last_person = session.query(Invitees).filter_by(relationship_with_sam24=status).order_by(Invitees.chair_number.desc()).first()

    if last_person:
        return last_person.chair_number + 1
    else:
        return 1


def send_message(receiver_gmail, subject, message):
    import smtplib
    from email.message import EmailMessage
    import os

    msg = EmailMessage()

    SMP_GMAIL = os.getenv('SMP_GMAIL')
    SMP_GMAIL_PW = os.getenv('SMP_GMAIL_PW')

    msg['Subject'] = subject
    msg['From'] = SMP_GMAIL
    msg['To'] = receiver_gmail
    msg.set_content(message, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SMP_GMAIL, SMP_GMAIL_PW)
        smtp.send_message(msg)


def generate_message(name, passcode):
    message = """
              <!DOCTYPE html>
              <html lang="en">
              <head>
                  <meta charset="UTF-8">
                  <meta name="viewport" content="width=device-width, initial-scale=1.0">
                  <title>SMP'24 Passcode Notification</title>
                      <style>
                          /* CSS styling for email */
                          body {
                              font-family: Arial, sans-serif;
                              background-color: #ffffff;
                              padding: 20px;
                              margin: 0;
                          }
                  
                          .container {
                              max-width: 600px;
                              margin: auto;
                              background-color: #050774;
                              padding: 40px;
                              box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                              border-top: 10px outset rgb(136, 114, 212);
                          }
                  
                          h1 {
                              color: #fcfcfc;
                              text-align: center;
                          }
                  
                          p {
                              color: #ffffff;
                              font-size: 16px;
                              line-height: 1.6;
                              margin-bottom: 20px;
                              font-weight: 500;
                          }
                  
                          .passcode {
                              background-color: #cec9c9;
                              border: 1px solid #ddd;
                              padding: 10px 20px;
                              font-size: 20px;
                              text-align: center;
                              margin-bottom: 20px;
                          }
                  
                          .footer {
                              text-align: center;
                              margin-top: 30px;
                              color: #999;
                          }
                      </style>
                  
                  
                  
                  
                  
                  
                  
                  
              </head>
    
    """ + f"""
    <body>
        <div class="container">
            <h1>SAM'24 Passcode Notification</h1>
            <p>Dear {name},</p>
            <p>We are excited to invite you to SMP'24! Below is your passcode for registration:</p>
            <div class="passcode">{passcode}</div>
            <p>Please ensure to safeguard this passcode as it will grant you access to the event.</p>
            <p>Thank you and we look forward to seeing you at the event!</p>
            <div class="footer">Best regards,<br> The SMP'24 Team</div>
        </div>
    </body>
    </html>
    """
    return message


if __name__ == '__main__':
    app.run(debug=True)
