from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import *
class UpdateFileSerializer(serializers.ModelSerializer):
    userid_id = serializers.IntegerField()
    userid=serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=updateFile
        fields=['id','userid','inputfile','create_at','userid_id']

class OutputFileSerializer(serializers.ModelSerializer):
    userid=serializers.PrimaryKeyRelatedField(read_only=True)
    userid_id=serializers.IntegerField()
    fileid=serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=outputFile
        fields=['id','userid','fileid','keyword','output_file','create_at','userid_id']

class UserInformationSerializer(serializers.ModelSerializer):
    userinputfile=UpdateFileSerializer(many=True,read_only=True)
    useroutfile=OutputFileSerializer(many=True,read_only=True)
    class Meta:
        model=userInformation
        fields=('id','name','password','filesize','stat','create_at','update_at','userinputfile','useroutfile')

