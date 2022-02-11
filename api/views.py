from django.db.models import query_utils
from django.shortcuts import render
from rest_framework import generics, serializers, status
from .serializers import RoomSerializer, CreateRoomSerializer,UpdateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse


class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

# APIView allow us, override default methods.We can define post,get methods


class GetRoom(APIView):
    serializer_class = RoomSerializer
    look_url_kwarg = 'code'

    def get(self, request, format=None):
        code = request.GET.get(self.look_url_kwarg)
        if code != None:
            room = Room.objects.filter(code=code)
            if len(room) > 0:
                data = RoomSerializer(room[0]).data
                data['is_host'] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code. '}, status=status.HTTP_404_NOT_FOUND)
        return Response({"Bad Request:", "Code parameter not found."}, status=status.HTTP_400_BAD_REQUEST)


class JoinRoom(APIView):
    look_url_kwarg = 'code'

    def post(self, request, format=None):
        # if current user in active session
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()  # if it doesn't create session
        code = request.data.get(self.look_url_kwarg)
        if code != None:
            room_result = Room.objects.filter(code=code)
            if len(room_result) > 0:
                room = room_result[0]
                # current session in this room
                self.request.session["room_code"] = code
                return Response({"message": "Room Joined!"}, status=status.HTTP_200_OK)
            return Response({"Bad Request": "Invalid Room"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"Bad Request": "Invalid post data, did not find a code"}, status=status.HTTP_404_NOT_FOUND)


class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer  # not mandatory

    def post(self, request, format=None):
        # if current user in active session
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()  # if it doesn't create session
        # take all of the data, if the data sent was valid.
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)
            if queryset.exists():  # update room
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                # current session
                self.request.session["room_code"] = room.code

                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            else:  # if we are not updating room then we are creating new one
                room = Room(host=host, guest_can_pause=guest_can_pause,
                            votes_to_skip=votes_to_skip)
                room.save()
                # current session
                self.request.session["room_code"] = room.code

                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)


class UserInRoom(APIView):
    def get(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        data = {
            'code': self.request.session.get('room_code')
        }
        return JsonResponse(data, status=status.HTTP_200_OK)


class LeaveRoom(APIView):
    def post(self, request, format=None):
        if 'room_code' in self.request.session:
            self.request.session.pop('room_code')
            host_id = self.request.session.session_key
            room_results = Room.objects.filter(host=host_id)
            if len(room_results) > 0:
                room = room_results[0]
                room.delete()

        return Response({'Message': 'Success'}, status=status.HTTP_200_OK)

class UpdateRoom(APIView):
    serializer_class = UpdateRoomSerializer

    def patch(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')

            queryset = Room.objects.filter(code=code)
            if not queryset.exists():
                return Response({'msg': 'Room does not exist'}, status=status.HTTP_404_NOT_FOUND)
            room = queryset[0]
            user_id = self.request.session.session_key
            if not self.request.session.exists(self.request.session.session_key):
                self.request.session.create()
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause','votes_to_skip'])
            return Response(RoomSerializer(room).data, status = status.HTTP_200_OK)

        return Response({'Bad Request': 'Invalid Data...'}, status=status.HTTP_400_BAD_REQUEST)