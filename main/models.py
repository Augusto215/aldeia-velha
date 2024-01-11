from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from datetime import datetime
import logging
from decimal import Decimal

from django.utils import timezone
from django.utils.timezone import timedelta
from django.utils.translation import gettext_lazy as _
import uuid
from django import forms
from PIL import Image
import requests
import datetime  # Importando o módulo datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator

from django.contrib.contenttypes.models import ContentType



